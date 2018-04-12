from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions
from twilio.rest import Client
import os
import json
import logging
import traceback
import time

# Logger
directory = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(directory, './logs/activity.log')
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

creds = list(line.strip() for line in open('./creds/creds.txt'))
account_sid = creds[0]
auth_token = creds[1]
twilio_client = Client(account_sid, auth_token)

phone_numbers = list(line.strip() for line in open('./creds/phone_numbers.txt'))
recipient = phone_numbers[0]
twilio_number = phone_numbers[1]

driver_path = os.path.join(directory, './WebDriver/chromedriver')


class DvcsClient():

	def check_availability(self, recipient_number, campus, term, course):
		try:
			options = webdriver.ChromeOptions()
			options.add_argument('--headless')
			driver = webdriver.Chrome(executable_path=driver_path, chrome_options=options)
			driver.get('https://webapps.4cd.edu/apps/CourseScheduleSearch/Default.aspx')

			campus_option = WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, "//input[@value='{0}']".format(campus))))
			driver.execute_script('arguments[0].click()', campus_option)
			terms = Select(driver.find_element_by_id('ctl00_PlaceHolderMain_SEC_TERM'))
			terms.select_by_visible_text(term)
			courses = Select(driver.find_element_by_id('ctl00_PlaceHolderMain_X_COURSE'))
			courses.select_by_visible_text(course)
			search = WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, "//input[@value='Search']")))
			driver.execute_script("arguments[0].click()", search)

			course_name_td = WebDriverWait(driver, 10).until(expected_conditions.presence_of_all_elements_located((By.XPATH, "//span[contains(text(), '{0}')]".format(course))))
			for td in course_name_td:
				course_tr = td.find_element_by_xpath('./../../..')
				cell = course_tr.find_element_by_xpath(".//td[8]")
				course_id_cell = course_tr.find_elements_by_tag_name("td")[2]
				course_id = course_id_cell.find_elements_by_tag_name("a")[0]

				if (cell.text == 'Open'):
					twilio_client.api.account.messages.create(
						to="{0}".format(recipient),
						from_="{0}".format(twilio_number),
						body="{0} ({1}) has a seat available!".format(course, course_id.text)
						)
					logging.info('Class has a seat available: text sent')
				elif (cell.text == 'Wlst'):
					twilio_client.api.account.messages.create(
						to="{0}".format(recipient),
						from_="{0}".format(twilio_number),
						body="{0} ({1}) has a spot on the waitlist!".format(course, course_id.text)
						)
					logging.info('Class has a waitlist seat available: text sent')
				else:
					logging.info('Class is full: no text sent')
		except Exception as e:
			print(str(traceback.format_exc()))
			logging.warning(str(traceback.format_exc()))


	def update_courses_list(self):
		try:
			options = webdriver.ChromeOptions()
			options.add_argument('--headless')
			driver = webdriver.Chrome(executable_path=driver_path, chrome_options=options)
			driver.get('https://webapps.4cd.edu/apps/CourseScheduleSearch/Default.aspx')

			campus = []
			terms = Select(driver.find_element_by_id('ctl00_PlaceHolderMain_SEC_TERM'))
			terms_list = [term.text for term in terms.options]
			terms_list.pop(0)
			
			terms_array = []
			dvc_campus = WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, "//input[@value='DVC']")))
			driver.execute_script('arguments[0].click()', dvc_campus)
			for term in terms_list:
				terms = Select(driver.find_element_by_id('ctl00_PlaceHolderMain_SEC_TERM'))
				terms.select_by_visible_text(term)
				dvc_courses = Select(driver.find_element_by_id('ctl00_PlaceHolderMain_X_COURSE'))
				courses = [course.text for course in dvc_courses.options]
				courses.pop(0)
				terms_array.append({'term': term, 'courses': courses})
			dvc_courses_json = {'name': 'DVC', 'terms': terms_array}

			terms_array = []
			src_campus = WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, "//input[@value='SRC']")))
			driver.execute_script('arguments[0].click()', src_campus)
			for term in terms_list:
				terms = Select(driver.find_element_by_id('ctl00_PlaceHolderMain_SEC_TERM'))
				terms.select_by_visible_text(term)
				src_courses = Select(driver.find_element_by_id('ctl00_PlaceHolderMain_X_COURSE'))
				courses = [course.text for course in src_courses.options]
				courses.pop(0)
				terms_array.append({'term': term, 'courses': courses})
			src_courses_json = {'name': 'SRC', 'terms': terms_array}

			all_courses_json = {'all_courses': {'campus': [dvc_courses_json, src_courses_json]}}

			with open('./data/courses.json', 'w') as outfile:
				json.dump(all_courses_json, outfile, indent=4)			
		except Exception as e:
			print(str(traceback.format_exc()))
			logging.warning(str(traceback.format_exc()))