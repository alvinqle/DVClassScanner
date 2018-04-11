from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys
from twilio.rest import Client

creds = list(line.strip() for line in open('./creds/creds.txt'))
account_sid = creds[0]
auth_token = creds[1]
twilio_client = Client(account_sid, auth_token)

recipient = ''
twilio_number = ''

def main():

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
	elif (cell.text == 'Wlst'):
		twilio_client.api.account.messages.create(
			to="{0}".format(recipient),
			from_="{0}".format(twilio_number),
			body="COMSC-200 has a spot on the waitlist!"
			)
	else:
		print('Course is full :(')

	driver.close()


if __name__ == '__main__':
	main()