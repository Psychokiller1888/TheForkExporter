import argparse
import re
import time
from dataclasses import dataclass
from typing import List, Optional

from dataclass_csv import DataclassWriter

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


@dataclass
class Customer:
	title: str = ''
	firstName: str = ''
	lastName: str = ''
	vip: bool = False
	birthDay: str = 1
	birthMonth: str = 1
	birthYear: str = 1900
	phone: str = ''
	email: str = ''
	language: str = 'fr'
	address: str = ''
	allergies: str = ''
	specialDiet: str = ''
	food: str = ''
	drinks: str = ''
	seating: str = ''
	notes: str = ''
	newsletter: bool = False
	reservations: int = 0
	cancellations: int = 0
	noShows: int = 0

class Job:
	def __init__(self):
		self.browser: Optional[Chrome] = None
		self.start()

	def start(self):
		print('Starting Chrome')
		options = Options()
		options.add_experimental_option(name='detach', value=True)
		self.browser = Chrome(options=options)
		self.browser.get('https://manager.thefork.com/')


	def getElement(self, by: By = By.CLASS_NAME, value: str = '', rootElement: Optional[WebElement] = None) -> Optional[WebElement]:
		if not rootElement:
			rootElement = self.browser
		try:
			return rootElement.find_element(by=by, value=value)
		except:
			return None


	def getElements(self, by: By = By.CLASS_NAME, value: str = '', rootElement: Optional[WebElement] = None) -> List[WebElement] | None:
		if not rootElement:
			rootElement = self.browser
		try:
			return rootElement.find_elements(by=by, value=value)
		except:
			return None


	def getInputValue(self, by: By = By.CLASS_NAME, value: str = '', rootElement: Optional[WebElement] = None) -> str:
		el = self.getElement(by=by, value=value, rootElement=rootElement)
		if not el:
			print(f'"{value}" not found')
			return ''

		value = el.get_property('value')
		if not value:
			return ''
		return value


	def getCheckboxValue(self, by: By = By.CLASS_NAME, value: str = '', rootElement: Optional[WebElement] = None) -> bool:
		el = self.getElement(by=by, value=value, rootElement=rootElement)
		if not el:
			print(f'"{value}" not found')
			return ''

		value = el.get_attribute('data-checked')
		if not value or value == 'false':
			return False

		return True


	def getElementInnerHTML(self, by: By = By.CLASS_NAME, value: str = '', rootElement: Optional[WebElement] = None, silent: bool = True) -> str:
		el = self.getElement(by=by, value=value, rootElement=rootElement)
		if not el:
			if not silent:
				print(f'"{value}" not found')
			return ''

		value = el.get_property('innerHTML')
		if not value:
			return ''

		return value


	def searchAndClick(self, by: By = By.CLASS_NAME, value: str = '', rootElement: Optional[WebElement] = None, wait: float = 1.0, noExit: bool = False, silent: bool = False) -> Optional[WebElement]:
		el: WebElement = self.getElement(by=by, value=value, rootElement=rootElement)
		if not el:
			if not silent:
				print(f'Cannot find element "{value}"')

			if noExit:
				return None
			else:
				exit(1)

		if not el.is_enabled():
			if not silent:
				print(f'Element is not active')

			if noExit:
				return None
			else:
				exit(1)

		self.click(el=el, wait=wait)
		return el

	@staticmethod
	def click(el: WebElement, wait: float = 1.0):
		el.click()
		time.sleep(wait)


	def extractData(self, url: str) -> Customer:
		self.browser.get(url)
		time.sleep(0.5)

		phonePrefix = '+ 41'
		phoneContainer = self.getElement(value='PIDgt')
		if phoneContainer:
			phonePrefix = self.getElementInnerHTML(value='DNVgs', rootElement=phoneContainer)
			match = re.search(r'\+ ([0-9]+)', phonePrefix)
			if match:
				phonePrefix = f'+{match.group(1)}'

		birthMonth = 'January'
		birthMonthContainer = self.getElement(value='tf-233int')
		if birthMonthContainer:
			birthMonth = self.getElementInnerHTML(value='chili-single-select__single-value', rootElement=birthMonthContainer)
			if not birthMonth:
				birthMonth = 'January'

		language = 'French'
		languageContainer = self.getElement(value='tf-1f6mg5w')
		if languageContainer:
			language = self.getElementInnerHTML(value='chili-single-select__single-value', rootElement=languageContainer)
			if not language:
				language = 'French'

		reservations = 0
		cancellations = 0
		noShows = 0
		customerBehaviors = self.getElements(value='tf-n7xbu5')
		for info in customerBehaviors:
			data = self.getElement(value='tf-1a9sr1e', rootElement=info).get_attribute('data-restaurant')
			if data:
				data = int(data)
			else:
				continue

			if info.get_property('innerHTML').endswith('reservations'):
				reservations = data
			elif info.get_property('innerHTML').endswith('cancellations'):
				cancellations = data
			elif info.get_property('innerHTML').endswith('no-shows'):
				noShows = data


		customer = Customer(
			title = 'mr',
			firstName = self.getInputValue(by=By.NAME, value='firstName'),
			lastName = self.getInputValue(by=By.NAME, value='lastName'),
			vip = self.getCheckboxValue(by=By.ID, value='vip'),
			birthDay = self.getInputValue(by=By.NAME, value='birthDate.day'),
			birthMonth = birthMonth,
			birthYear = self.getInputValue(by=By.NAME, value='birthDate.year'),
			phone = f'{phonePrefix} {self.getInputValue(by=By.NAME, value="phone")}',
			email = self.getInputValue(by=By.NAME, value='email'),
			language = language,
			address = self.getInputValue(by=By.CLASS_NAME, value='addressAutocomplete__input'),
			newsletter = self.getCheckboxValue(by=By.ID, value='optin'),
			allergies = '',
			specialDiet = '',
			food = self.getInputValue(by=By.NAME, value='favFood'),
			drinks = self.getInputValue(by=By.NAME, value='favDrinks'),
			seating = self.getInputValue(by=By.NAME, value='favSeating'),
			notes = self.getInputValue(by=By.NAME, value='notesOnCustomer'),
			reservations = reservations,
			cancellations = cancellations,
			noShows = noShows
		)
		return customer



if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='TheFork customer data extractor', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('-u', '--user', help='TheFork account user', required=True, type=str)
	parser.add_argument('-p', '--password', help='TheFork account password', required=True, type=str)
	parser.add_argument('-d', '--debug', help='Limit the extracted data to 15 customers', required=False, type=bool)
	args = parser.parse_args()
	config = vars(args)

	EMAIL = config['user']
	PASSWORD = config['password']
	DEBUG = config['debug']

	job = Job()

	element = job.getElement(value='tf-15l7y55')
	print('Please solve the Google ReCaptcha manually if any pops up')
	while not element:
		job.searchAndClick(value='evidon-banner-acceptbutton', noExit=True, silent=True)
		username = job.getElement(by=By.NAME, value='username')
		if username and not username.get_property('value'):
			username.send_keys(EMAIL)

		password = job.getElement(by=By.NAME, value='password')
		if password and not password.get_property('value'):
			password.send_keys(PASSWORD)

		job.searchAndClick(value='tf-1p32jew', noExit=True, silent=True)

		time.sleep(1)
		element = job.getElement(value='tf-15l7y55')

	print('Logged in! Now let me do the job, don\'t touch the browser!')

	job.searchAndClick(value='tf-ehlden') #search button
	job.searchAndClick(value='tf-1aex8qq', wait=2) #advanced search

	urls = set()


	while True:
		for link in job.getElements(value='kzMV1'):
			if DEBUG and len(urls) > 14:
				break
			url = link.get_attribute('href')
			urls.add(url)

		if DEBUG and len(urls) > 14:
			break

		try:
			spans = job.getElements(value='mask')
			if not spans:
				raise Exception()

			button = None
			for span in spans:
				if span.get_attribute('innerHTML') != 'Next':
					continue

				button = span.find_element(by=By.XPATH, value='..')
				break

			if button:
				if button.is_enabled():
					job.click(button, 2)
				else:
					raise Exception()
			else:
				raise Exception()
		except:
			print('That was the last page!')
			break

	print(f'Found {len(urls)} customers')
	print('Start data extraction')

	customers = list()
	for url in urls:
		data = job.extractData(url)
		customers.append(data)

	print(f'Extracted {len(customers)} customers')
	print('Dumping to csv')

	with open('data.csv', 'w') as fp:
		writer = DataclassWriter(fp, customers, Customer)
		writer.write()

	print('All done!')