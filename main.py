import argparse
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict

from dataclass_csv import DataclassWriter

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

import chromedriver_autoinstaller


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
	def __init__(self, confs: Dict):
		self.browser: Optional[Chrome] = None
		self.config = confs
		chromedriver_autoinstaller.install()
		self.start()

	def start(self):
		print('Connecting Chrome')
		options = Options()
		options.add_experimental_option('debuggerAddress', f'localhost:{self.config["port"]}')
		self.browser = Chrome(options=options)


	def getElement(self, by: By = By.CLASS_NAME, value: str = '', rootElement: Optional[WebElement] = None) -> Optional[WebElement]:
		if not rootElement:
			rootElement = self.browser
		try:
			return rootElement.find_element(by=by, value=value)
		except:
			return None


	def getElements(self, by: By = By.CLASS_NAME, value: str = '', rootElement: Optional[WebElement] = None) -> Optional[List[WebElement]]:
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


	def getCheckboxValue(self, by: By = By.CLASS_NAME, value: str = '', rootElement: Optional[WebElement] = None) -> Optional[bool]:
		el = self.getElement(by=by, value=value, rootElement=rootElement)
		if not el:
			print(f'"{value}" not found')
			return None

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


	def extractData(self, url: str, tries: int = 0, browse: bool = True) -> Optional[Customer]:
		if tries < 5:
			if browse:
				self.browser.get(url)
				time.sleep(0.75)

			phonePrefix = '+ 41'
			phoneContainer = self.getElement(value='y6YeV')
			if phoneContainer:
				phonePrefix = self.getElementInnerHTML(value='DNVgs', rootElement=phoneContainer)
				match = re.search(r'\+ ([0-9]+)', phonePrefix)
				if match:
					phonePrefix = f'+{match.group(1)}'
			else:
				print('Page not yet loaded, retry')
				time.sleep(0.25)
				return self.extractData(url=url, tries= tries + 1, browse=False)

			birthMonth = 'January'
			birthMonthContainer = self.getElement(value='tf-1hwfws3')
			if birthMonthContainer:
				birthMonth = self.getElementInnerHTML(value='chili-single-select__single-value', rootElement=birthMonthContainer)
				if not birthMonth:
					birthMonth = 'January'

			language = 'French'
			languageContainer = self.getElement(value='tf-1hwfws3')
			if languageContainer:
				language = self.getElementInnerHTML(value='chili-single-select__single-value', rootElement=languageContainer)
				if not language:
					language = 'French'

			reservations = 0
			cancellations = 0
			noShows = 0

			customerBehaviors = self.getElements(value='tf-q2scvx')
			for info in customerBehaviors:
				data = self.getElement(value='tf-1enwdf5', rootElement=info).get_attribute('data-restaurant')
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
		else:
			raise



if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='TheFork customer data extractor', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('-u', '--port', help='Remote debugging prot', required=False, type=int, default=9222)
	parser.add_argument('-d', '--debug', help='Limit the extracted data to 15 customers', required=False, type=bool)
	parser.add_argument('-l', '--load', help='Load customers from file', required=False, type=bool, default=False)
	args = parser.parse_args()
	config = vars(args)

	PORT = config['port']
	DEBUG = config['debug']
	LOAD = config['load']

	job = Job(config)

	print('Let me do the job, don\'t touch the browser!')
	urls = set()

	if not LOAD:
		job.searchAndClick(by=By.XPATH, value='//*[@id="mainContent"]/div[1]/div[1]/div[3]/div/div[1]/button') #search button
		job.searchAndClick(value='tf-zl9zk6', wait=2) #advanced search

		i = 1
		retry_rows = 0
		retry = 0
		while True:
			print(f'Reading page {i}')
			for link in job.getElements(value='e3st0'):
				if DEBUG and len(urls) > 14:
					break
				url = link.get_attribute('href')
				result = re.search(r'https://manager\.thefork\.com/customer/(.+)/\?prevPathname=/search', url)
				if result:
					urls.add(f'https://manager.thefork.com/customer/{result.group(1)}/details')

			if DEBUG and len(urls) > 14:
				break

			try:
				spans = job.getElements(value='mask')
				if not spans:
					retry_rows += 1
					if retry_rows < 10:
						print('Button row not found, trying again')
						time.sleep(0.5)
						continue

					raise Exception()

				button = None
				for span in spans:
					if span.get_attribute('innerHTML') != 'Next':
						continue

					button = span.find_element(by=By.XPATH, value='..')
					break

				if button:
					if button.is_enabled():
						i += 1
						retry = 0
						retry_rows = 0
						job.click(button, 0.5)
					else:
						retry += 1
						if retry < 10:
							print('Button found but not enabled, trying again')
							time.sleep(0.5)
							continue
						raise Exception()
				else:
					retry += 1
					if retry < 10:
						print('Failed finding button, trying again')
						time.sleep(0.5)
						continue
					else:
						raise Exception()
			except:
				print('That was the last page!')
				break
	else:
		if Path('urls.txt').exists():
			urls = Path('urls.txt').read_text().splitlines()

	print(f'Found {len(urls)} customers')

	if not LOAD:
		print('Writing list to file')
		with open('urls.txt', 'w') as fp:
			for url in urls:
				fp.write(f'{url}\n')

	print('Start data extraction')

	customers = list()
	for url in urls:
		try:
			data = job.extractData(url)
			customers.append(data)
		except:
			print(f'Failed extracting data for customer on url {url}')

	print(f'Extracted {len(customers)} customers')
	print('Dumping to csv')

	with open('data.csv', 'w') as fp:
		writer = DataclassWriter(fp, customers, Customer)
		writer.write()

	print('All done!')