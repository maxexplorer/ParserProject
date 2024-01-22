import requests
from bs4 import BeautifulSoup


url = "https://www.ozon.ru/"


response = requests.get(url=url)
print(response)
soup = BeautifulSoup(response.text, 'lxml')
item = soup.find('h1', class_='zm0')
print(item)

with open('index.html', 'w', encoding='utf-8') as file:
    file.write(response.text)