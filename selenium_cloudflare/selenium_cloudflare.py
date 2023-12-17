from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

# options = webdriver.ChromeOptions()
# is equivalent to
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

service = Service()
driver = webdriver.Chrome(service=service, options=options)

driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    'source': '''
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
  '''
})

try:
    driver.maximize_window()
    driver.get(url="https://tokensniffer.com/")

    # element = driver.find_element(By.CSS_SELECTOR, 'label.ctp-checkbox-label')
    time.sleep(5)
    print(driver.page_source)
    # element = driver.find_element(By.CSS_SELECTOR, 'input[type=checkbox]')
    # time.sleep(50)
    # print(element)


except Exception as ex:
    print(ex)
finally:
    driver.close()
    driver.quit()
