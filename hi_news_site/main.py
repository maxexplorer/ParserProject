import requests
from bs4 import BeautifulSoup
import os
import time
import json


headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0'
                  ' Safari/537.36'
}

start_time = time.time()

if not os.path.exists('data'):
    os.mkdir('data')


def get_articles_urls():
    article_url_list = []

    with requests.Session() as session:
        page = 1
        while True:
            url = f'https://hi-news.ru/tag/robototexnika/page/{page}'

            response = session.get(url=url, headers=headers)

            soup = BeautifulSoup(response.text, 'lxml')
            pagination = soup.find_all(class_="page-item")

            article_url = soup.find_all('a', class_='more-link')

            for au in article_url:
                art_url = au.get('href')
                article_url_list.append(art_url)

            print(page)
            page += 1

            if 'active' in str(pagination[-1]):
                with open('data/articles_urls.txt', 'w', encoding='utf-8') as file:
                    print(*article_url_list, file=file, sep='\n')

                return f'Обработано {page - 1} страниц!'


def get_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        url_list = [line.strip() for line in file.readlines()]

    urls_count = len(url_list)
    result_data = []

    with requests.Session() as session:
        for i, url in enumerate(url_list, 1):
            response = session.get(url=url, headers=headers)
            soup = BeautifulSoup(response.text, 'lxml')
            try:
                article_title = soup.find('h1', class_="single-title").text.strip()
                article_author = soup.find('a', class_='author').text.strip()
                article_date = soup.find(class_='post__date-inner').text.strip()
                article_img = soup.find('div', class_='text').find('img').get('src')
                article_text = ''.join([item.text.strip() for item in soup.find('div', class_='text').find_all('p')])

                result_data.append(
                    {
                        'original_url': url,
                        'article_title': article_title,
                        'article_author': article_author,
                        'article_date': article_date,
                        'article_img': article_img,
                        'article_text': article_text
                    }
                )
            except Exception as ex:
                print(ex)

            print(f'Обработано {i}/{urls_count}')

    with open('data/result.json', 'w', encoding='utf-8') as file:
        json.dump(result_data, file, indent=4, ensure_ascii=False)


def main():
    # print(get_articles_urls())
    get_data('data/articles_urls.txt')
    finish_time = time.time() - start_time
    print(f'Время работы программы: {finish_time}')


if __name__ == '__main__':
    main()
