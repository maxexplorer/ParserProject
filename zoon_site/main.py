import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
import os

url = "https://zoon.ru/msk/hotels/"


# options
options = webdriver.ChromeOptions()

# change useragent
useragent = UserAgent()
options.add_argument(f'user-agent={useragent.random}')


def get_search_html(url):
    driver = webdriver.Chrome(
        executable_path="C:/Users/Макс/PycharmProjects/ParserProject/chromedriver/chromedriver.exe",
        options=options,
    )
    driver.maximize_window()

    try:
        driver.get(url=url)
        time.sleep(3)

        while True:
            find_more_element = driver.find_element(By.CLASS_NAME, 'catalog-button-showMore')
            if driver.find_elements(By.CLASS_NAME, 'hasmore-text'):
                with open('data/page_source.html', 'w', encoding='utf-8') as file:
                    file.write(driver.page_source)
                break
            else:
                actions = ActionChains(driver)
                actions.move_to_element(find_more_element).perform()
                time.sleep(3)

        # SCROLL_PAUSE_TIME = 3
        #
        # # Get scroll height
        # last_height = driver.execute_script("return document.body.scrollHeight")
        #
        # while True:
        #     # Scroll down to bottom
        #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        #
        #     # Wait to load page
        #     time.sleep(SCROLL_PAUSE_TIME)
        #
        #     # Calculate new scroll height and compare with last scroll height
        #     new_height = driver.execute_script("return document.body.scrollHeight")
        #     if new_height == last_height:
        #         with open('data/page_source.html', 'w', encoding='utf-8') as file:
        #             file.write(driver.page_source)
        #         break
        #     last_height = new_height
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


def main():
    get_search_html(url=url)


if __name__ == '__main__':
    main()
