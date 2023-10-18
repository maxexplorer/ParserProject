import requests
import random
import string
import time
import os

API = 'https://www.1secmail.com/api/v1/'
domain_list = [
    "1secmail.com",
    "1secmail.org",
    "1secmail.net",
    "wwjmp.com",
    "esiix.com",
    "xojxe.com",
    "yoggm.com"
]
domain = random.choice(domain_list)


def generate_username():
    name = string.ascii_lowercase + string.digits
    username = ''.join(random.choice(name) for i in range(10))

    return username


def check_mail(mail=''):
    req_link = f'{API}?action=getMessages&login={mail.split("@")[0]}&domain={mail.split("@")[-1]}'
    response = requests.get(req_link).json()
    length = len(response)

    if length == 0:
        print('Новых писем нет!')
    else:
        id_list = [v for k, v in response.items() if k == 'id']
        print(f'у Вас {length} новых писем!')





def delete_mail():
    pass


def main():
    try:
        username = generate_username()
        mail = f'{username}@{domain}'
        print(mail)

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print('Программа прервана!')


if __name__ == '__main__':
    main()
