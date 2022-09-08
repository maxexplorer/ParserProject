import requests
from bs4 import BeautifulSoup
import json
import os


def get_first_news():
    url = "https://www.securitylab.ru/news/"
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/104.0.0.0 Safari/537.36'
    }

    r = requests.get(url=url, headers=headers)

    soup = BeautifulSoup(r.text, 'lxml')

    news_dict = {}

    try:
        articles_cards = soup.find_all(class_='article-card')

        for article in articles_cards:
            article_title = article.find('h2', class_='article-card-title').text.strip()
            article_desc = article.find('p').text.strip()
            article_url = f"https://www.securitylab.ru{article.get('href')}"
            article_date_time = article.find('time').text
            article_id = article_url.split('/')[-1][:-4]

            news_dict[article_id] = {
                'article_date_time': article_date_time,
                'article_url': article_url,
                'article_title': article_title,
                'article_desc': article_desc
            }


    except Exception as ex:
        print(ex)

    if not os.path.exists('data'):
        os.mkdir('data')

    with open('data/news_dict.json', 'w', encoding='utf-8') as file:
        json.dump(news_dict, file, indent=4, ensure_ascii=False)


def check_news_update():
    with open('data/news_dict.json', 'r', encoding='utf-8') as file:
        news_dict = json.load(file)

    url = "https://www.securitylab.ru/news/"
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/104.0.0.0 Safari/537.36'
    }

    r = requests.get(url=url, headers=headers)

    soup = BeautifulSoup(r.text, 'lxml')

    fresh_news = {}

    try:
        articles_cards = soup.find_all(class_='article-card')

        for article in articles_cards:
            article_url = f"https://www.securitylab.ru{article.get('href')}"
            article_id = article_url.split('/')[-1][:-4]

            if article_id in news_dict:
                continue
            else:
                article_title = article.find('h2', class_='article-card-title').text.strip()
                article_desc = article.find('p').text.strip()
                article_date_time = article.find('time').text

            news_dict[article_id] = {
                'article_date_time': article_date_time,
                'article_url': article_url,
                'article_title': article_title,
                'article_desc': article_desc
            }

            fresh_news[article_id] = {
                'article_date_time': article_date_time,
                'article_url': article_url,
                'article_title': article_title,
                'article_desc': article_desc
            }

    except Exception as ex:
        print(ex)

    with open('data/news_dict.json', 'w', encoding='utf-8') as file:
        json.dump(news_dict, file, indent=4, ensure_ascii=False)

    return fresh_news


def main():
    get_first_news()
    print(check_news_update())


if __name__ == '__main__':
    main()
