import requests
from datetime import datetime


start_time = datetime.now()

url = "https://www.sofascore.com/ru/tennis/rankings/atp"

headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                  ' (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931'
}


# Получаем html разметку страницы
def get_html(url: str, headers: dict, session: requests.sessions.Session) -> str:
    """
    :param url: str
    :param headers: dict
    :param session: requests.sessions.Session
    :return: str
    """

    try:
        response = session.get(url=url, headers=headers, timeout=60)

        if response.status_code != 200:
            print(response.status_code)

        html = response.text
        return html
    except Exception as ex:
        print(ex)



def main():
    main()

if __name__ == '__main__':
    main()

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')
