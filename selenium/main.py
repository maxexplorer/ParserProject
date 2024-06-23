from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from undetected_chromedriver import Chrome as undetectedChrome
from undetected_chromedriver import ChromeOptions


from fake_useragent import UserAgent


useragent = UserAgent().random


# Создаём объект chromedriver
def init_chromedriver(headless_mode: bool = False) -> Chrome:
    options = Options()
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
    options.add_argument("--disable-blink-features=AutomationControlled")
    if headless_mode:
        options.add_argument("--headless=new")
    driver = Chrome(options=options)
    if not headless_mode:
        driver.maximize_window()
    driver.implicitly_wait(15)

    return driver

# Создаём объект undetected_chromedriver
def init_undetected_chromedriver(headless_mode=False):
    if headless_mode:
        options = ChromeOptions()
        options.add_argument('--headless')
        driver = undetectedChrome(options=options)
        driver.implicitly_wait(15)
    else:
        driver = undetectedChrome()
        driver.maximize_window()
        driver.implicitly_wait(15)
    return driver

def main():
    init_chromedriver()



if __name__ == '__main__':
    main()
