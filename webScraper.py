#This webscraper was written for educational purposes only. Respect terms of use of indivual websites when webscraping!

#IMPORT PACKAGES

import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install("selenium")
install("bs4")
install("requests")

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as soup
import random
import time
import requests

#SET INPUTS TO SPECIFY WHICH DATA TO SCRAPE

search = "Arzt"
location = "Hamburg"
pageLength = 228
chromeDriver = '/Users/PATH_TO_CHROME_DRIVER'

#OPEN CHROMEDRIVE TO HANDLE "LOADMORE" BUTTON

seconds = 2 + (random.random() * 2)
url = 'https://www.gelbeseiten.de/Suche/{search}/{location}'

driver_path = chromeDriver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--incognito")

driver = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)
driver.get(url)

time.sleep(seconds)

cookies = driver.find_element_by_xpath("//a[@class='cmpboxbtn cmpboxbtnyes']").click()

time.sleep(seconds)
time.sleep(seconds)

for i in range(pageLength):
    element = driver.find_element_by_xpath("//a[@id='mod-LoadMore--button']")
    driver.execute_script("arguments[0].click();", element)
    time.sleep(seconds)
html = driver.page_source


#EXTRACT LINKS FROM FRONTPAGE

data = soup(html, "html.parser")

import re
linkArr = []

for pages in data.findAll('a', attrs={'href': re.compile("^https://www.gelbeseiten")}):
	link = pages.get('href')
	linkArr.append(link)
	

#GO THROUGH LINKS AND EXTRACT DATA

url2 = 'www.gelbeseiten.de'
fieldHierarchy = 'h2'
fieldItem = "data-wipe-name"
fieldName = "Titel"

def callItem(url2, fieldHierarchy, fieldItem, fieldName):
	try:
		 response = requests.get(url2, timeout=5)
		 content = soup(response.content, "html.parser")
		 return content.find(fieldHierarchy, attrs={fieldItem: fieldName}).text
	except (AttributeError, requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
		"n/a"

doctorArr = []

for doctor in linkArr:
	doctorObject = {
		"name": callItem(doctor,'h3', "class", "gc-text--h3 contains-icon-name"),
		"address": callItem(doctor, 'p', "class", "mod-Kontaktdaten__list-item"),
		"phone": callItem(doctor, 'a', "class", "nolink-black"),
		"e-mail": callItem(doctor, 'li', "class", "mod-Kontaktdaten__list-item contains-icon-email"),
		"homepage": callItem(doctor, 'li', "class", "mod-Kontaktdaten__list-item contains-icon-homepage")
	}
	doctorArr.append(doctorObject)


#EXTRACT TO EXCEL

import pandas as pd
df = pd.DataFrame(doctorArr).T
df.to_excel(excel_writer = "webScraper.xlsx")

