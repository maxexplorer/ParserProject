import json
import re
import time
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

useragent = UserAgent()

# url = "https://www.avito.ru/web/5/user/aea431590bda05adb724a8a071d0e0c9/ratings"
url = "https://www.avito.ru/web/5/user/14f1abec03bee090ac28e8fbc09f2ab8/ratings?limit=25&offset=25&sortRating=date_desc&summary_redesign=1"

options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")

browser = webdriver.Chrome(options=options)

# browser.add_cookie(cookie_dict=cookies)

browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    'source': '''
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
  '''
})
browser.maximize_window()


try:
    browser.get(url=url)
    time.sleep(5)
    src = browser.page_source

except Exception as ex:
    print(ex)

finally:
    browser.close()
    browser.quit()

# res_dict = json.loads(src.lstrip('<html><head><meta name="color-scheme" content="light dark"></head><body><pre style="word-wrap:'
#                  ' break-word; white-space: pre-wrap;">').rstrip('</pre></body></html>'))

soup = BeautifulSoup(src, 'lxml')


json_data = soup.find('pre').text
print(json.loads(json_data))

