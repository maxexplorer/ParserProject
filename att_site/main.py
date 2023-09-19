from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
import time

useragent = UserAgent()

options = Options()
options.add_argument(useragent.random)
options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option('useAutomationExtension', False)

service = Service(executable_path="D:\\PycharmProjects\\ParserProject\\chromedriver\\chromedriver.exe")
browser = webdriver.Chrome(service=service, options=options)

browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    'source': '''
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
  '''
})

try:
    browser.maximize_window()
    browser.get(url="https://www.att.com/deviceunlock/unlockstep1")
    time.sleep(10)
    try:
        radio_button = browser.find_element(By.CSS_SELECTOR, 'input.radioBtnOpacity')
        radio_button.click()
    except Exception as ex:
        print(ex)
    try:
        imei_number = browser.find_element(By.CSS_SELECTOR, '#imeino')
        imei_number.send_keys('Hello')
    except Exception as ex:
        print(ex)
except Exception as ex:
    print(ex)
finally:
    browser.close()
    browser.quit()
