import argparse
import json
import time

import requests

import queries
import sqlite3

parser = argparse.ArgumentParser(description='TheFork customer data extractor', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-i', '--id', help='Your restaurant id', required=True, type=str)
parser.add_argument('-t', '--token', help='Your authorization token', required=True, type=str)
parser.add_argument('-d', '--debug', help='Limit the extracted data to 15 customers', required=False, type=bool, default=False)
parser.add_argument('-f', '--fresh', help='Fetch all customer data anew, not only the new ones', required=False, type=bool, default=False)
parser.add_argument('-r', '--resume', help='Resume with only the customers that have no data filled', required=False, type=bool, default=False)
parser.add_argument('-s', '--history', help='Fetch the reservation history for existing customers', required=False, type=bool, default=False)
args = parser.parse_args()
config = vars(args)

DEBUG = config['debug']
RESTAURANT_ID = config['id']
AUTH_TOKEN = config['token']
FRESH = config['fresh']
RESUME = config['resume']
HISTORY = config['history']


URL = 'https://manager.thefork.com/api/graphql'
headers = {
	'Authorization': f'Bearer {AUTH_TOKEN}'
}

if __name__ == '__main__':
	con = sqlite3.connect('database.sqlite')
	cursor = con.cursor()

	try:
		cursor.execute('''
			CREATE TABLE IF NOT EXISTS customers(
				id TEXT PRIMARY KEY UNIQUE,
				civility TEXT,
				firstName TEXT,
				lastName TEXT,
				email TEXT,
				phone TEXT,
				secondaryPhone TEXT,
				locale TEXT,
				notes TEXT,
				optin INTEGER,
				restaurantOptin TEXT,
				allergiesAndIntolerances TEXT,
				status TEXT,
				isPromoter INTEGER,
				rank TEXT,
				computedRank TEXT,
				isVip INTEGER,
				dietaryRestrictions TEXT,
				bookingCount INTEGER,
				customerReliabilityScore INTEGER,
				recentNoShowCount INTEGER,
				recentBookingCount INTEGER,
				favFood TEXT,
				favDrinks TEXT,
				favSeating TEXT,
				birthDate TEXT,
				address TEXT,
				reservations INTEGER,
				cancellations INTEGER,
				noShows INTEGER,
				groupReservations INTEGER,
				groupCancellations INTEGER,
				groupNoShows INTEGER,
				lastUpdated INTEGER
			)
		''')
		con.commit()
	except sqlite3.Error as e:
		print(f'Issues with database, cannot continue: {e}')
		exit(1)

	try:
		cursor.execute('''
			CREATE TABLE IF NOT EXISTS history(
				id TEXT PRIMARY KEY UNIQUE,
				isOnline TEXT,
				bookingOrigin TEXT,
				mealDate TEXT,
				status TEXT,
				partySize INTEGER,
				tableName TEXT,
				customerNote TEXT,
				restaurantNote TEXT,
				occasions TEXT,
				tables TEXT,
				promoter TEXT,
				customer TEXT,
				offerSnapshot TEXT,
				menu TEXT,
				`order` TEXT,
				isBurningYums INTEGER,
				imprint TEXT,
				restaurantUuid TEXT,
				restaurant TEXT,
				review TEXT
			)
		''')
		con.commit()
	except sqlite3.Error as e:
		print(f'Issues with database, cannot continue: {e}')
		exit(1)

	if DEBUG:
		print('DEBUG MODE')

	if HISTORY:
		uuids = list()
		existingReservations = list()

		print('Loading existing history')
		cursor.execute(f'SELECT id FROM history')
		results = cursor.fetchall()
		for result in results:
			existingReservations.append(result[0])

		print(f'Loaded {len(existingReservations)} historic reservations')

		print('Loading customers')
		cursor.execute(f'SELECT id FROM customers {"LIMIT 15" if DEBUG else ""}')
		results = cursor.fetchall()
		for result in results:
			uuids.append(result[0])

		print(f'Loaded {len(uuids)} customers ids')

		count = 0
		customerCount = 0
		for uuid in uuids:
			customerCount += 1
			print(f'\rFetching history for customer {customerCount} ({uuid})', end='')
			variables = {
				"restaurantId": RESTAURANT_ID,
				"customerId": uuid,
				"onGroup": False,
				"orderBy": {
					"column": "mealDate",
					"direction": "desc"
				}
			}
			response = requests.post(
				url=URL,
				json={
					'query':     queries.GET_CUSTOMER_HISTORY,
					'variables': variables
				},
				headers=headers
			)
			try:
				reservations = response.json()['data']['customerReservations']
			except:
				continue

			for i, reservation in enumerate(reservations):
				if reservation['id'] in existingReservations:
					# As we query the history by date desc, as soon as we hit an id already existing, we know the rest is already in our database
					break
				count += 1

				cursor.execute('REPLACE INTO history (id, isOnline, bookingOrigin, mealDate, status, partySize, tableName, customerNote, restaurantNote, occasions, tables, promoter, customer, offerSnapshot, menu, `order`, isBurningYums, imprint, restaurantUuid, restaurant, review) VALUES (:id, :isOnline, :bookingOrigin, :mealDate, :status, :partySize, :tableName, :customerNote, :restaurantNote, :occasions, :tables, :promoter, :customer, :offerSnapshot, :menu, :order, :isBurningYums, :imprint, :restaurantUuid, :restaurant, :review)',
				               {
					               'id':             reservation['id'],
					               'isOnline':       reservation['isOnline'],
					               'bookingOrigin':  reservation['bookingOrigin'],
					               'mealDate':       reservation['mealDate'],
					               'status':         reservation['status'],
					               'partySize':      reservation['partySize'],
					               'tableName':      reservation['tableName'],
					               'customerNote':   reservation['customerNote'],
					               'restaurantNote': reservation['restaurantNote'],
					               'occasions':      json.dumps(reservation['occasions']),
					               'tables':         json.dumps(reservation['tables']),
					               'promoter':       json.dumps(reservation['promoter']),
					               'customer':       json.dumps(reservation['customer']),
					               'offerSnapshot':  json.dumps(reservation['offerSnapshot']),
					               'menu':           json.dumps(reservation['menu']),
					               'order':          json.dumps(reservation['order']),
					               'isBurningYums':  reservation['isBurningYums'],
					               'imprint':        json.dumps(reservation['imprint']),
					               'restaurantUuid': reservation['restaurantUuid'],
					               'restaurant':     json.dumps(reservation['restaurant']),
					               'review':         json.dumps(reservation['review'])
				               })
				con.commit()
		print('')
		print(f'Inserted a total of {count} historic reservations')
	else:
		print('Loading existing customers')
		existingUuids = list()
		newUuids = list()

		if not FRESH:
			cursor.execute('SELECT id FROM customers')
			results = cursor.fetchall()
			for result in results:
				existingUuids.append(result[0])

		print('Fetching uuids, please wait....')
		sortings = [
			[],
			[
				"customerFirstName",
				"customerLastName"
			],
			[
				"-customerFirstName",
				"-customerLastName"
			]
			,
			[
				"-customerFirstName",
				"customerLastName"
			],
			[
				"customerFirstName",
				"-customerLastName"
			],
			[
				"reservationMealDate",
				"reservationMealTime"
			],
			[
				"-reservationMealDate",
				"-reservationMealTime"
			],
			[
				"-reservationMealDate",
				"reservationMealTime"
			],
			[
				"reservationMealDate",
				"-reservationMealTime"
			]
		]

		if not RESUME:
			for j, sorting in enumerate(sortings):
				# noinspection PyRedeclaration
				wasCount = len(newUuids)
				y = 100 if not DEBUG else 15

				for i in range (0, 10000, 100):
					print(f'\rScanning {15 if DEBUG else 100} customers at offset {i}', end='')
					variables = {
						"args": {
							"restaurantId": RESTAURANT_ID,
							"text": "",
							"sort": sorting,
							"filters": {},
							"highlight": True,
							"pagination": {
								"offset": i,
								"first": y
							}
						}
					}

					response = requests.post(
						url=URL,
						json={
							'query': queries.SEARCH_CUSTOMERS,
							'variables': variables
						},
						headers=headers
					)

					for result in response.json()['data']['searchCustomers']['results']:
						uid = result['customer']['id']
						if uid not in existingUuids and uid not in newUuids:
							newUuids.append(uid)

					if DEBUG:
						break

				print(f'Fetching method {j + 1} found {len(newUuids) - wasCount} new customers')
				wasCount = len(newUuids)

				if DEBUG:
					break


			print(f'Found {len(newUuids)} new customer')

			print('Writing list to database')
			for uid in newUuids:
				cursor.execute(
					'INSERT INTO customers (id) VALUES (:id)',
					{
						'id': uid
					}
				)
			con.commit()
		else:
			if not DEBUG:
				cursor.execute('SELECT id FROM customers WHERE lastUpdated IS NULL')
				results = cursor.fetchall()
				for result in results:
					newUuids.append(result[0])
			else:
				cursor.execute('SELECT id FROM customers WHERE lastUpdated IS NULL LIMIT 15')
				results = cursor.fetchall()
				for result in results:
					newUuids.append(result[0])

			print(f'Found {len(newUuids)} customers to fetch')

		i = 1
		if newUuids:
			print('Fetching customer information, please be patient')

			for uuid in newUuids:
				print(f'\rFetching customer #{i}', end='')
				variables = {
					'id': uuid
				}
				response = requests.post(
					url=URL,
					json={
						'query':     queries.GET_CUSTOMER,
						'variables': variables
					},
					headers=headers
				)

				customerData = response.json()['data']['customer']

				variables = {
					"id":             uuid,
					"restaurantUuid": RESTAURANT_ID,
					"withSpending":   True
				}
				response = requests.post(
					url=URL,
					json={
						'query':     queries.GET_CUSTOMER_STATS,
						'variables': variables
					},
					headers=headers
				)

				customerStats = response.json()['data']['customer']['reservationStats']

				cursor.execute(
					'REPLACE INTO customers (id, civility, firstName, lastName, email, phone, secondaryPhone, locale, notes, optin, restaurantOptin, allergiesAndIntolerances, status, isPromoter, rank, computedRank, isVip, dietaryRestrictions, bookingCount, customerReliabilityScore, recentNoShowCount, recentBookingCount, favFood, favDrinks, favSeating, birthDate, address, reservations, cancellations, noShows, groupReservations, groupCancellations, groupNoShows, lastUpdated) VALUES (:id, :civility, :firstName, :lastName, :email, :phone, :secondaryPhone, :locale, :notes, :optin, :restaurantOptin, :allergiesAndIntolerances, :status, :isPromoter, :rank, :computedRank, :isVip, :dietaryRestrictions, :bookingCount, :customerReliabilityScore, :recentNoShowCount, :recentBookingCount, :favFood, :favDrinks, :favSeating, :birthDate, :address, :reservations, :cancellations, :noShows, :groupReservations, :groupCancellations, :groupNoShows, :lastUpdated)',
					{
						'id':                       uuid,
						'civility':                 customerData['civility'],
						'firstName':                customerData['firstName'],
						'lastName':                 customerData['lastName'],
						'email':                    customerData['email'],
						'phone':                    customerData['phone'],
						'secondaryPhone':           customerData['secondaryPhone'],
						'locale':                   customerData['locale'],
						'notes':                    customerData['notes'],
						'optin':                    1 if customerData['optin'] else 0,
						'restaurantOptin':          json.dumps(customerData['restaurantOptin']),
						'allergiesAndIntolerances': json.dumps(customerData['allergiesAndIntolerances']),
						'status':                   customerData['status'],
						'isPromoter':               customerData['isPromoter'],
						'rank':                     customerData['rank'],
						'computedRank':             customerData['computedRank'],
						'isVip':                    1 if customerData['isVip'] else 0,
						'dietaryRestrictions':      json.dumps(customerData['dietaryRestrictions']),
						'bookingCount':             customerData['bookingCount'],
						'customerReliabilityScore': customerData['customerReliabilityScore'],
						'recentNoShowCount':        customerData['recentNoShowCount'],
						'recentBookingCount':       customerData['recentBookingCount'],
						'favFood':                  customerData['favFood'],
						'favDrinks':                customerData['favDrinks'],
						'favSeating':               customerData['favSeating'],
						'birthDate':                customerData['birthDate'],
						'address':                  customerData['address'],
						'reservations':             customerStats['reservationRecordedCount'],
						'cancellations':            customerStats['reservationCanceledCount'],
						'noShows':                  customerStats['reservationNoShowCount'],
						'groupReservations':        customerStats['reservationRecordedCountForGroup'],
						'groupCancellations':       customerStats['reservationCanceledCountForGroup'],
						'groupNoShows':             customerStats['reservationNoShowCountForGroup'],
						'lastUpdated':              round(time.time())
					}
				)
				con.commit()
				i += 1
	con.close()

	print('All done!')