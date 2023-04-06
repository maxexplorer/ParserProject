import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from datetime import datetime

start_time = datetime.now()


useragent = UserAgent()

headers = {
    'accept': '*/*',
    'user-agent': useragent.random
}


def get_urls():
    region = 'region77'
    page = 'page1'

    url = f"https://auto.drom.ru/{region}/all/{page}/"

    # response = requests.get(url=url, headers=headers)

    # with open('data/index.html', 'w', encoding='utf-8') as file:
    #     file.write(response.text)

    with open('data/index.html', 'r', encoding='utf-8') as file:
        html = file.read()

    soup = BeautifulSoup(html, 'lxml')

    urls_page = soup.find('div', class_='css-1nvf6xk eojktn00').find_next().find_all('a')

    url_list = []

    for item in urls_page:
        url = item.get('href')
        url_list.append(url)

    with open('data/url_list.txt', 'w', encoding='utf-8') as file:
        print(*url_list, file=file, sep='\n')


def get_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        url_list = [line.strip() for line in file.readlines()]

    with requests.Session() as session:
        for i, url in enumerate(url_list[:2], 1):
            response = session.get(url=url, headers=headers)
            with open('data/index_page.html', 'w', encoding='utf-8') as file:
                file.write(response.text)
            # soup = BeautifulSoup(response.text, 'lxml')
            #
            # title = soup.find(class_='css-1kb7l9z e162wx9x0').text.strip()
            # price = soup.find(class_='css-eazmxc e162wx9x0').text.strip()
            # print(title, price)




def main():
    # get_urls()
    get_data('data/url_list.txt')
    execution_time = datetime.now() - start_time
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
