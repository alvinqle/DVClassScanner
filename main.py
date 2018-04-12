from dvcs_client import DvcsClient
import os
import json
import logging
import traceback


# Logger
directory = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(directory, './logs/activity.log')
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

DvcsClient = DvcsClient()


def main():

	try:
		DvcsClient.check_availability('+15551234567', 'DVC', '2018SU', 'COMSC-165')
	except Exception as e:
		logging.warning(str(traceback.format_exc()))


if __name__ == '__main__':
	main()