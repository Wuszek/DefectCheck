import argparse
import getpass
import os.path
import sys
import time
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

elem_search_xpath = "element_to_search"
timeout = 5
website = "website.com/browse/"
elem_present_xpath = "element_to_be_present"


class DefectCheck:

    def __init__(self):
        self.driver = None

    def set_up(self):
        chrome_options = Options()
        if not setup:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument(
            f"--user-data-dir=C:\\Users\\{getpass.getuser()}\\AppData\\Local\\Google\\Chrome\\User Data\\Default")
        s = Service(ChromeDriverManager().install())
        chrome_options.add_argument("--profile-directory=Default")
        self.driver = webdriver.Chrome(service=s, options=chrome_options)
        if setup:
            '''
            Now yoy have 30 seconds to log in to that webpage, if your task requires being logged in. 
            '''
            self.driver.get("https://www.website.com")
            time.sleep(30)

    def loadExcel(self, file_xlsx):
        load = pd.read_excel(f"{file_xlsx}", 'Test run')
        prepared = load.drop(load.index[:8]) # drop 8 rows, including "title row"
        linklist = prepared["Unnamed: 5"].to_list()
        linklist = [x for x in linklist if str(x) != 'nan']  # remove empty values
        linklist = list(dict.fromkeys(linklist))  # remove duplicates
        for i, x in enumerate(linklist):  # create defect links from defect title
            linklist[i] = f"{website}{x.split(' ', 1)[0]}"
        return linklist

    def checkClosed(self, link_list, new_list=[]):
        for i in link_list:
            self.driver.get(f'https://{i}')
            try:
                element_present = EC.presence_of_element_located((By.XPATH, f"{elem_present_xpath}"))
                WebDriverWait(self.driver, timeout).until(element_present)
                self.driver.find_element(By.XPATH, elem_search_xpath)
                new_list.append(i)
                print(f"DEBUG : Issue {i} is closed!")
            except NoSuchElementException:
                print(f"ERROR : No element found on {i}")
                pass
            except TimeoutException:
                print(f"ERROR : Timeout exceeded. Page {i} not loaded correctly.")
                pass
        return new_list

    def listClosed(self, closed_list):
        print(f"\nList of closed defects:\n------------------------------------------------------")
        f = open('closed.txt', 'w')
        for i in closed_list:
            f.write(i+'\n')
        print("DEBUG : Writing list of closed defects to file finished.")
        f.close()

    def teardown(self):
        self.driver.close()

    def getOpt(self, argv):

        def isfile_check(path):
            if not os.path.isfile(f'{path}'):
                raise argparse.ArgumentTypeError("%s does not exist or path is broken." % path)
            return path

        parser = argparse.ArgumentParser \
            (usage="python3 main.py [-h] -i <file_path>",
             description="Description",
             epilog="© 2022, wiktor.kobiela", prog="DefectCheck",
             add_help=False,
             formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=120, width=250))

        required = parser.add_argument_group('required arguments')
        helpful = parser.add_argument_group('helpful arguments')

        required.add_argument('-i', action='store', dest="file", required=True, metavar="<path>",
                              help='Provide path to excel file generated from validationsraports', type=isfile_check)
        helpful.add_argument('-s', action='store_true', dest="setup", help="Login to portal to store credentials",
                             default=False)
        helpful.add_argument('-h', action='help', help='show this help message and exit')

        args = parser.parse_args()
        return args.file, args.setup

    def run(self, input_file):
        self.set_up()
        links = self.loadExcel(input_file)
        closed_list = self.checkClosed(links)
        self.listClosed(closed_list)
        self.teardown()


check = DefectCheck()
file, setup = check.getOpt(sys.argv[1:])
if setup:
    check.set_up()
    check.teardown()
else:
    check.run(file)

