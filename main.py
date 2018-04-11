from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys
from twilio.rest import Client
import os
import logging
import traceback

# Logger
directory = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(directory, './logs/activity.log')
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
logging.debug(logger)

creds = list(line.strip() for line in open('./creds/creds.txt'))
account_sid = creds[0]
auth_token = creds[1]
twilio_client = Client(account_sid, auth_token)

recipient = ''
twilio_number = ''

def main():

	try:
		driver = webdriver.Chrome()
		driver.get('https://webapps.4cd.edu/apps/CourseScheduleSearch/Default.aspx')
		campus = WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, "//input[@value='DVC']")))
		driver.execute_script('arguments[0].click()', campus)
		term = Select(driver.find_element_by_id('ctl00_PlaceHolderMain_SEC_TERM'))
		term.select_by_visible_text('2018SU')
		subject = Select(driver.find_element_by_id('ctl00_PlaceHolderMain_X_SUBJ'))
		subject.select_by_visible_text('COMSC - Computer Science (DVC & LMC)')
		search = WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, "//input[@value='Search']")))
		driver.execute_script("arguments[0].click()", search)

		course_id_td = WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, "//a[text()='{0}']".format(5047))))
		course_tr = course_id_td.find_element_by_xpath('./../../..')
		cell = course_tr.find_elements_by_tag_name("td")[12]

		if (cell.text == 'Open'):
			twilio_client.api.account.messages.create(
				to="{0}".format(recipient),
				from_="{0}".format(twilio_number),
				body="COMSC-200 has a seat available!"
				)
			logging.info('Class has a seat available: text sent')
		elif (cell.text == 'Wlst'):
			twilio_client.api.account.messages.create(
				to="{0}".format(recipient),
				from_="{0}".format(twilio_number),
				body="COMSC-200 has a spot on the waitlist!"
				)
			logging.info('Class has a waitlist seat available: text sent')
		else:
			logging.info('Class is full: no text sent')

		driver.close()
	except Exception as e:
		logging.warning(str(traceback.format_exc()))


if __name__ == '__main__':
	main()