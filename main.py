import argparse
import getpass
import os.path
import sys
import time
from sys import platform

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

ELEM_SEARCH_XPATH = "//span[@id='status-val']/span[.='Closed']"
TIMEOUT = 5
WEBSITE = "jira.atlassian.com/browse/"
ELEM_PRESENT_XPATH = "//span[@id='status-val']"
DEFECT_NAME_XPATH = "//h1[@id='summary-val']"
TYPE_VALUE = "//span[@id='type-val']"


class DefectCheck:

    def __init__(self):
        self.driver = None

    def set_up(self):
        chrome_options = Options()
        if not setup:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument('--no-sandbox')
        if platform == "linux" or platform == "linux2":
            chrome_options.add_argument(f"--user-data-dir=~/.config/google-chrome")
            s = Service('drivers/chromedriver')
        elif platform == "win32":
            chrome_options.add_argument(f"--user-data-dir=C:\\Users\\{getpass.getuser()}\\AppData\\Local\\Google\\Chrome\\User Data\\Default")
            s = Service('drivers/chromedriver.exe')
        chrome_options.add_argument("--profile-directory=Default")
        self.driver = webdriver.Chrome(service=s, options=chrome_options)
        if setup:
            self.driver.get("https://jira.atlassian.com/")
            time.sleep(30)

    def loadExcel(self, file):
        load = pd.read_excel(f"{file}", 'Test run')  # open tab named "Test run"
        prepared = load.drop(load.index[:8])  # drop 9 rows, including "title row"
        linklist = prepared["Unnamed: 5"].to_list()  # take 6th collumn
        linklist = [x for x in linklist if str(x) != 'nan']  # remove empty values
        for i, x in enumerate(linklist):  # create defect links from defect title
            # linklist[i] = f"{website}{x.split(' ', 1)[0]}"
            linklist[i] = f"{WEBSITE}{x[:9]}"  # workaround, as titles are sometimes broken. Update when counter >100k
        linklist = list(dict.fromkeys(linklist))  # remove duplicates
        print(f"-------------------------------------------------------")
        print(f"INFO \t: Loaded file {file}. Found {len(linklist)} unique defects. Looking for CLOSED:".expandtabs(15))
        print(f"-------------------------------------------------------")
        return linklist

    def checkClosed(self, link_list, new_list=[]):
        for i in link_list:
            self.driver.get(f'https://{i}')
            try:
                element_present = EC.presence_of_element_located((By.XPATH, f"{ELEM_PRESENT_XPATH}"))
                WebDriverWait(self.driver, TIMEOUT).until(element_present)
                type_d = self.driver.find_element(By.XPATH, TYPE_VALUE).text  # look for type
                self.driver.find_element(By.XPATH, ELEM_SEARCH_XPATH)  # look for status
                title = self.driver.find_element(By.XPATH, DEFECT_NAME_XPATH).text  # grab title
                closed_defect_info = f"{i} | Type: {type_d} | Title: {title}"
                new_list.append(closed_defect_info)
                print(f"{link_list.index(i) + 1}/{len(link_list)} INFO \t: {type_d} https://{i} "
                      f"is CLOSED! TITLE: {title}".expandtabs(5))
            except NoSuchElementException:
                defect_status = self.driver.find_element(By.XPATH, ELEM_PRESENT_XPATH).text
                print(f"{link_list.index(i) + 1}/{len(link_list)} ERROR \t: {type_d} https://{i} "
                      f"is {defect_status}".expandtabs(5))
                pass
            except TimeoutException:
                print(f"{link_list.index(i) + 1}/{len(link_list)} ERROR \t: Timeout exceeded. "
                      f"Page https://{i} not loaded correctly.".expandtabs(5))
                pass
        return new_list

    def listClosed(self, closed_list, input_file):
        print(f"-------------------------------------------------------")
        f = open(f'{input_file[:-5]}.txt', 'w')
        closed_list.sort()
        for i in closed_list:
            f.write(f'https://{i}' + '\n')
        f.close()
        print(f"INFO \t: Writing list of closed defects to {input_file[:-5]}.txt finished.".expandtabs(15))
        print(f"-------------------------------------------------------")

    def teardown(self):
        self.driver.close()

    def getOpt(self, argv):

        def isfile_check(path):
            if not os.path.isfile(f'{path}'):
                raise argparse.ArgumentTypeError("%s does not exist or path is broken." % path)
            return path

        parser = argparse.ArgumentParser \
            (usage="python3 main.py [-h -s] -i <file_path>",
             description="Description",
             epilog="© 2022, wiktor.kobiela", prog="DefectCheck",
             add_help=False,
             formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=120, width=250))

        required = parser.add_argument_group('required arguments')
        helpful = parser.add_argument_group('helpful arguments')

        required.add_argument('-i', action='store', dest="file", required=True, metavar="<path>",
                              help='Provide path to excel file generated from website.com', type=isfile_check)
        helpful.add_argument('-s', action='store_true', dest="setup", help="Login to portal to store credentials",
                             default=False)
        helpful.add_argument('-h', action='help', help='show this help message and exit')

        args = parser.parse_args()
        return args.file, args.setup

    def run(self, input_file):
        self.set_up()
        links = self.loadExcel(input_file)
        closed_list = self.checkClosed(links)
        self.listClosed(closed_list, input_file)


check = DefectCheck()
file, setup = check.getOpt(sys.argv[1:])
if setup:
    try:
        check.set_up()
        check.teardown()
    except Exception:
        check.teardown()
else:
    try:
        check.run(file)
        check.teardown()
    except Exception:
        check.teardown()
