import requests


def request_without_proxy():
    """Запрос без прокси"""
    response = requests.get(url="https://api.myip.com")
    print("Без прокси:", response.json(), '\n')


def request_with_proxy():
    """Запрос с использованием прокси в формате user:pass@ip:port"""
    proxies = {
        'http': 'http://X7FiXtGT:V5xWAQSP@146.19.110.223:64304',
        'https': 'http://X7FiXtGT:V5xWAQSP@146.19.110.223:64304',
    }
    response = requests.get(url="https://api.myip.com", proxies=proxies)
    print("С прокси:", response.json())


request_without_proxy()
request_with_proxy()
