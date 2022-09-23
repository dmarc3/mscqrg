import os
from time import sleep
import ipdb
# import requests
from bs4 import BeautifulSoup as bs
from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from requests_html import HTMLSession
from pprint import pprint

URL = 'https://help.hexagonmi.com/bundle/MSC_Nastran_2022.3/page/Nastran_Combined_Book/qrg/bulkab/TOC.ACCEL.xhtml'

options = FirefoxOptions()
options.add_argument("--headless")
browser = Firefox(
    executable_path=os.path.join(os.path.dirname(__file__), 'geckodriver'),
    options=options,
    )
browser.get(URL)
html = browser.execute_script("return document.body")
sleep(10)
article = html.find_element('tag name', 'article')
tables = article.find_elements('tag name', 'table')

# Print results:
for i, table in enumerate(tables):
    ipdb.set_trace()
soup = bs(html, "html.parser")