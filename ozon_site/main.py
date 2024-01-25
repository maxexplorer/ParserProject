import time

from undetected_chromedriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup




def undetected_chromdriver():

    driver = Chrome()
    driver.maximize_window()
    driver.implicitly_wait(15)

    try:
        driver.get(url="https://ozon.ru/t/601oMbY")

        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, 'lxml')

        price = ''.join(filter(lambda x: x.isdigit(), soup.find('span', class_='lm5 l3m').text))

        storage = None


        # print(driver.page_source)

        basket = driver.find_element(By.XPATH, '//*[@id="layoutPage"]/div[1]/div[4]/div[3]/div[2]/div[2]/div/div/div[3]/div/div/div[1]/div/div/div/div[1]/button')
        basket.click()

        WebDriverWait(driver, 15).until(
            EC.text_to_be_present_in_element((By.XPATH, '//*[@id="layoutPage"]/div[1]/div[4]/div[3]/div[2]/div[2]/div/div/div[3]/div/div/div[1]/div/div/div/div[1]/button/div[1]/div/span[1]'), 'В корзине')
        )

        in_basket = driver.find_element(By.XPATH, '//*[@id="layoutPage"]/div[1]/div[4]/div[3]/div[2]/div[2]/div/div/div[3]/div/div/div[1]/div/div/div/div[1]/button')
        in_basket.click()

        quantity = driver.find_element(By.CSS_SELECTOR, 'input[inputmode = numeric]').get_attribute('max')

        button_del1 = driver.find_element(By.XPATH, '//*[@id="layoutPage"]/div[1]/div/div/div[2]/div[4]/div[1]/div/div/div[1]/div[1]/button')

        button_del1.click()

        button_del2 = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div/div[2]/div/div/section/div[3]/button'))
        )

        button_del2.click()
        time.sleep(10)


    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()

def get_data():
    pass

def main():
    undetected_chromdriver()


if __name__ == '__main__':
    main()
