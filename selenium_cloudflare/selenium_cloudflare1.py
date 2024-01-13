import undetected_chromedriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import time

driver = undetected_chromedriver.Chrome()
driver.maximize_window()
options = Options()
useragent = UserAgent().random
options.add_argument(f'User-Agent={useragent}')
options.add_argument("--disable-blink-features=AutomationControlled")
driver = undetected_chromedriver.Chrome(options=options)
driver.maximize_window()

try:
    # driver.get(url="https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html")
    driver.get(url="https://www.sneakersnstuff.com/")
    time.sleep(15)
except Exception as ex:
    print(ex)
finally:
    driver.close()
    driver.quit()
