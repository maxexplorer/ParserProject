from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os
import time

# options = webdriver.ChromeOptions()
# is equivalent to
options = Options()
# options.add_argument('User-Agent = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
#                          ' Chrome/108.0.0.0 Safari/537.36')

options.add_argument("--headless")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

service = Service(executable_path="C:/Users/Макс/PycharmProjects/ParserProject/chromedriver/chromedriver.exe")
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
    driver.get(url="https://www.similarweb.com/ru/website/tvnz.co.nz/#overview")
    time.sleep(10)
    data = driver.page_source
except Exception as ex:
    print(ex)
finally:
    driver.close()
    driver.quit()

if not os.path.exists('data'):
    os.mkdir('data')

with open('data/html_data.html', 'w', encoding='utf-8') as file:
    file.write(data)



