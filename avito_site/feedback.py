import json
import re
import time
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

useragent = UserAgent()

# url = "https://www.avito.ru/web/5/user/aea431590bda05adb724a8a071d0e0c9/ratings"
url = "https://www.avito.ru/web/5/user/14f1abec03bee090ac28e8fbc09f2ab8/ratings?limit=25&offset=25&sortRating=date_desc&summary_redesign=1"
cookies = {
    'srv_id': '2dVlr7UyN1nDJYyd.fJy_kzHU6kEuyG4AxawEI-tWEYmAi3Xf-fOpb7Luao3bkXtb0ls5fX4_0iBC_Lc=.EpJJEowwMbGYEj6EtsW-f-1FqrQuKYEFiVM080FHSuY=.web',
    'u': '2y4prus9.qdx0p7.1gh4ezdrsxw00',
    '_gcl_au': '1.1.993755952.1698135811',
    'tmr_lvid': 'f8d7f626b9d8120f24a0d6b1ac217a79',
    'tmr_lvidTS': '1698135811329',
    '_ga': 'GA1.1.1538377045.1698135811',
    'advcake_session_id': '1ede7707-5072-47fc-df95-2a3633742051',
    'adrcid': 'AqO_0h3xzskulSUJF8stxzw',
    'buyer_laas_location': '656350',
    '_ym_uid': '1698135891434220681',
    '_ym_d': '1698135891',
    'yandex_monthly_cookie': 'true',
    'uxs_uid': 'cd8a3c90-7246-11ee-a8ad-61acfbb396f1',
    '__zzatw-avito': 'MDA0dBA=Fz2+aQ==',
    '__zzatw-avito': 'MDA0dBA=Fz2+aQ==',
    'buyer_popup_location': '0',
    'auth': '1',
    'advcake_click_id': '',
    '_ga_9NLSMYFRV5': 'GS1.1.1698780863.1.1.1698780873.0.0.0',
    'gMltIuegZN2COuSe': 'EOFGWsm50bhh17prLqaIgdir1V0kgrvN',
    'advcake_utm_partner': 'perf_yd_b2b_comn_all_site_sea_b_030323_brand-geo',
    'advcake_track_id': '01587148-d157-6a75-2431-95670c0b2cee',
    'advcake_track_url': 'https%3A%2F%2Fwww.avito.ru%2Fbusiness%3Futm_medium%3Dcpc%26utm_source%3Dyandex%26avito_campaign_id%3D84002449%26utm_campaign%3Dperf_yd_b2b_comn_all_site_sea_b_030323_brand-geo%26utm_content%3D5143327952_13603472562%26utm_term%3D%25D0%25B0%25D0%25B2%25D0%25B8%25D1%2582%25D0%25BE%2520%25D0%25BC%25D0%25BE%25D1%2581%25D0%25BA%25D0%25B2%25D0%25B0_desktop_%25D0%259C%25D0%25BE%25D1%2581%25D0%25BA%25D0%25B2%25D0%25B0%26idfa%3D%26gps_adid%3D%26oaid%3D%26adjust_t%3Doxuwg2_bkgc5n%26adjust_campaign%3Dperf_yd_b2b_comn_all_site_sea_b_030323_brand-geo%26adjust_adgroup%3D84002449%26adjust_creative%3D13603472562_%25D0%25B0%25D0%25B2%25D0%25B8%25D1%2582%25D0%25BE%2520%25D0%25BC%25D0%25BE%25D1%2581%25D0%25BA%25D0%25B2%25D0%25B0_5143327952%26adjust_ya_click_id%3D35478458687553535%26etext%3D%26yclid%3D6506428688754875076',
    'advcake_utm_webmaster': '5143327952_13603472562',
    'cfidsw-avito': 'Momn8ku1WkRYMhAsO2+eJ4r1Wo/qmq8RtSnB0KvufLMyZWB1oYz/204kFIYK0ueS+kRrZPXKeh3QY4ZCrF34CxUXNS3A4o8aPknM13HKuCrpxnxsHFIYs23R++LreXlHcGsT7yWCVW3Ta437mRRNmlUY8+mTxhOrkb8Xmg==',
    'cfidsw-avito': 'Momn8ku1WkRYMhAsO2+eJ4r1Wo/qmq8RtSnB0KvufLMyZWB1oYz/204kFIYK0ueS+kRrZPXKeh3QY4ZCrF34CxUXNS3A4o8aPknM13HKuCrpxnxsHFIYs23R++LreXlHcGsT7yWCVW3Ta437mRRNmlUY8+mTxhOrkb8Xmg==',
    'gsscw-avito': '8BUSxUDREJLWmfrHrm/0btzvvhKLzfwqTscNXuDpPR3odscrZrIeWS9/CkqglRXWfeEFNeTWXWMTdcmnvhVS6FnvjCyGBiCzY/Gsrb030cPbWYvgFfhk1WSp4XADRNd4ZWMfwje3GWP+eFOh2TFWmP7hcN/rphBKaj9bo66Js67fbkp1XOuWMtkL3zIGLWzKw+MTygRs+nb1OQhEPepy0OSjIzOG7fd0PKQAjY8H1/QdyFCFNrtRnOe+wwX5rg==',
    'gsscw-avito': '8BUSxUDREJLWmfrHrm/0btzvvhKLzfwqTscNXuDpPR3odscrZrIeWS9/CkqglRXWfeEFNeTWXWMTdcmnvhVS6FnvjCyGBiCzY/Gsrb030cPbWYvgFfhk1WSp4XADRNd4ZWMfwje3GWP+eFOh2TFWmP7hcN/rphBKaj9bo66Js67fbkp1XOuWMtkL3zIGLWzKw+MTygRs+nb1OQhEPepy0OSjIzOG7fd0PKQAjY8H1/QdyFCFNrtRnOe+wwX5rg==',
    'cfidsw-avito': 'sIF3V/0529sIxYnt6lMfYeH1xBNWANit8qDaQnVvfZrxfrVr2MGIFZB5kjwRpx4OW1FqE0GyEd6SF4+b0DQRRvhLyRRG7ZmQ+Qh5WPSZv/Fbl9RfDrfxX0Omojoxjc9fDKE1kkbY7N+GUQX9yjpON8kRBnoWco4Aa1U/Bg==',
    'fgsscw-avito': 'Ea7755df6a127af1e6c47a65fd0056f7c42e2811',
    'fgsscw-avito': 'Ea7755df6a127af1e6c47a65fd0056f7c42e2811',
    '_ym_isad': '2',
    'f': '5.0c4f4b6d233fb90636b4dd61b04726f147e1eada7172e06c47e1eada7172e06c47e1eada7172e06c47e1eada7172e06cb59320d6eb6303c1b59320d6eb6303c1b59320d6eb6303c147e1eada7172e06c8a38e2c5b3e08b898a38e2c5b3e08b890df103df0c26013a7b0d53c7afc06d0b2ebf3cb6fd35a0ac0df103df0c26013a8b1472fe2f9ba6b9e2bfa4611aac769efa4d7ea84258c63d59c9621b2c0fa58f915ac1de0d034112ad09145d3e31a56946b8ae4e81acb9fae2415097439d4047fb0fb526bb39450a46b8ae4e81acb9fa34d62295fceb188dd99271d186dc1cd03de19da9ed218fe2d50b96489ab264edd50b96489ab264edd50b96489ab264ed46b8ae4e81acb9fa38e6a683f47425a8352c31daf983fa077a7b6c33f74d335cb88de1666d503ec6255f55f36b9873b31d49c1c93fcdfd74c97fa6b2200ff95afc0488193561305817c7721dca45217bb350872d8cb7fbbb7f1988ff29cf017746b8ae4e81acb9fa46b8ae4e81acb9fa02c68186b443a7ac401959c92f93565f1769115734d9269b2da10fb74cac1eab2da10fb74cac1eab25037f810d2d41a8134ecdeb26beb8b53778cee096b7b985bf37df0d1894b088',
    'ft': '"Tw1+by1lWI7Vsgfum2H+vFwRzM/1ATgWgX/ums7g5IXcPlXbs7U/dg5/k6aourRjbGdOY7OGmewEdmK5IZTtV03IGzNR34/P+z0hbp0DN1Wx74omSCPeVxdECdlwm2Cob+B6+f1M4GgvVhKymbp4Xx1CIO3FDm7bdYPdCC0CXmrzZGWr++5OCU0Pp5FTt0u4"',
    'cto_bundle': 'ewXK6194VFU1NHREcG5xJTJGYm1hcnBERzA1dEwwaDJKSHI5dzcwRlZDUHppQXlIQThEMm9iUDVUdWMlMkZOZUZudGtjMHFqZGIlMkZweU54bXp0JTJCWTRsNml2ZUxMdjQzZVRhVkFMNE1vRE1pZWVmOXMwdWdqUjA5M3p6M0ZVdG96NFB0UGx4M1BzWEh2UFVISUZHc0pLWVVwU0VYYWYxUjJWanMlMkJrd2I2eGxDd0cyYUc3bHdUSWxSb0laOHRFd3hCZFhNdGtCU3JXVmlvTGlaaGZzc3V1UTdWcCUyRmIxOUpjSEJQNURxNGVXOWw4RjNiZVZZYWh4NW1hNUtGQlFYQWklMkJzUVdjMUFFMks',
    '_ga_WW6Q1STJ8M': 'GS1.1.1699037156.5.0.1699037160.0.0.0',
    '_ga_ZJDLBTV49B': 'GS1.1.1699037156.5.0.1699037160.0.0.0',
    'v': '1699079141',
    '_ym_visorc': 'b',
    'SEARCH_HISTORY_IDS': '4%2C',
    'luri': 'nizhniy_novgorod',
    'buyer_location_id': '640860',
    'dfp_group': '9',
    '_buzz_fpc': 'JTdCJTIycGF0aCUyMiUzQSUyMiUyRiUyMiUyQyUyMmRvbWFpbiUyMiUzQSUyMi53d3cuYXZpdG8ucnUlMjIlMkMlMjJleHBpcmVzJTIyJTNBJTIyTW9uJTJDJTIwMDQlMjBOb3YlMjAyMDI0JTIwMDclM0EwNyUzQTM3JTIwR01UJTIyJTJDJTIyU2FtZVNpdGUlMjIlM0ElMjJMYXglMjIlMkMlMjJ2YWx1ZSUyMiUzQSUyMiU3QiU1QyUyMnVmcCU1QyUyMiUzQSU1QyUyMjQxZWE5OGQwZmJlYzAxYzE4ZjU0ZTYwNzA3MGMxZDE4JTVDJTIyJTJDJTVDJTIyYnJvd3NlclZlcnNpb24lNUMlMjIlM0ElNUMlMjIxMTkuMCU1QyUyMiU3RCUyMiU3RA==',
    'abp': '0',
    '_ga_M29JC28873': 'GS1.1.1699079145.14.1.1699081684.7.0.0',
    'sx': 'H4sIAAAAAAAC%2F6STS3brOAxE96KxB%2BAPILIbECCd548ky09ypBztvY8HTsc97Q3cqlO4%2BO4cMDF6cQKRpLIWNG%2FBqXei7Ev38d0t3UdXILmaWqQGMWTnsliuKsGalSYtk0sKytwdutp9OGR2mJDCfuicE64Fg2uh5JiiFG01aWYzzt7lV0RzMDHwiZe0yECfjPFyoc88eOjnZfhNzpDjfui8E1CkUipripCjRp8TG7nmG0v%2BX%2BUJ%2BBlhxD6FkhIxk8taQ%2FSAKBZqc0SviLM%2FKs9treso6VHGcFvndQu9z2V6TNM7mdN%2B6IJQDpx9y%2BhMQShoKFZycdpYXHqRt96W802Py1XcNpYyJhlsjtuKl2v48m%2FkFHE%2FdBG0omdlH6OpLxmsRShckUspJbzIXgI2Zbo9btAqbt5Nk%2BQ%2Fkl1r%2FXh7Hzz4%2FdChi06JqBXRZOhqVvIUs8YYqpMfW5C%2F5nH0VT%2Fp%2FAnGj3mZfOivJ%2Bjv43b%2FTcaYnmsgIqoRNkZOGJErlRrYKIEqGb%2FI62WeeFY%2FHo9h%2Fvvo18vUc70Pf6drfzuf3zv7vB86DdZqqSJsahJqacqxKjEGlhZ%2BOsPVTrfrOX1t96UtAMXuemZdTo9%2B2P78uiDkSPFJNqbYHFhQqVqBOYccvTlG4BjzjxtgcR34caNjGxC30zKhmCA8%2F26w%2F4gdntY1SCq5SCZDTCGlytXVwgEykYr7d41NWgYAG%2FDq%2FRhOC%2FA6DtaKcYJ3Nzjt%2Bz8BAAD%2F%2F6JlbtTxAwAA',
    'tmr_detect': '0%7C1699081687388',
}

headers = {
    'authority': 'www.avito.ru',
    'accept': 'application/json',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/json',
    # 'cookie': 'srv_id=2dVlr7UyN1nDJYyd.fJy_kzHU6kEuyG4AxawEI-tWEYmAi3Xf-fOpb7Luao3bkXtb0ls5fX4_0iBC_Lc=.EpJJEowwMbGYEj6EtsW-f-1FqrQuKYEFiVM080FHSuY=.web; u=2y4prus9.qdx0p7.1gh4ezdrsxw00; _gcl_au=1.1.993755952.1698135811; tmr_lvid=f8d7f626b9d8120f24a0d6b1ac217a79; tmr_lvidTS=1698135811329; _ga=GA1.1.1538377045.1698135811; advcake_session_id=1ede7707-5072-47fc-df95-2a3633742051; adrcid=AqO_0h3xzskulSUJF8stxzw; buyer_laas_location=656350; _ym_uid=1698135891434220681; _ym_d=1698135891; yandex_monthly_cookie=true; uxs_uid=cd8a3c90-7246-11ee-a8ad-61acfbb396f1; __zzatw-avito=MDA0dBA=Fz2+aQ==; __zzatw-avito=MDA0dBA=Fz2+aQ==; buyer_popup_location=0; auth=1; advcake_click_id=; _ga_9NLSMYFRV5=GS1.1.1698780863.1.1.1698780873.0.0.0; gMltIuegZN2COuSe=EOFGWsm50bhh17prLqaIgdir1V0kgrvN; advcake_utm_partner=perf_yd_b2b_comn_all_site_sea_b_030323_brand-geo; advcake_track_id=01587148-d157-6a75-2431-95670c0b2cee; advcake_track_url=https%3A%2F%2Fwww.avito.ru%2Fbusiness%3Futm_medium%3Dcpc%26utm_source%3Dyandex%26avito_campaign_id%3D84002449%26utm_campaign%3Dperf_yd_b2b_comn_all_site_sea_b_030323_brand-geo%26utm_content%3D5143327952_13603472562%26utm_term%3D%25D0%25B0%25D0%25B2%25D0%25B8%25D1%2582%25D0%25BE%2520%25D0%25BC%25D0%25BE%25D1%2581%25D0%25BA%25D0%25B2%25D0%25B0_desktop_%25D0%259C%25D0%25BE%25D1%2581%25D0%25BA%25D0%25B2%25D0%25B0%26idfa%3D%26gps_adid%3D%26oaid%3D%26adjust_t%3Doxuwg2_bkgc5n%26adjust_campaign%3Dperf_yd_b2b_comn_all_site_sea_b_030323_brand-geo%26adjust_adgroup%3D84002449%26adjust_creative%3D13603472562_%25D0%25B0%25D0%25B2%25D0%25B8%25D1%2582%25D0%25BE%2520%25D0%25BC%25D0%25BE%25D1%2581%25D0%25BA%25D0%25B2%25D0%25B0_5143327952%26adjust_ya_click_id%3D35478458687553535%26etext%3D%26yclid%3D6506428688754875076; advcake_utm_webmaster=5143327952_13603472562; cfidsw-avito=Momn8ku1WkRYMhAsO2+eJ4r1Wo/qmq8RtSnB0KvufLMyZWB1oYz/204kFIYK0ueS+kRrZPXKeh3QY4ZCrF34CxUXNS3A4o8aPknM13HKuCrpxnxsHFIYs23R++LreXlHcGsT7yWCVW3Ta437mRRNmlUY8+mTxhOrkb8Xmg==; cfidsw-avito=Momn8ku1WkRYMhAsO2+eJ4r1Wo/qmq8RtSnB0KvufLMyZWB1oYz/204kFIYK0ueS+kRrZPXKeh3QY4ZCrF34CxUXNS3A4o8aPknM13HKuCrpxnxsHFIYs23R++LreXlHcGsT7yWCVW3Ta437mRRNmlUY8+mTxhOrkb8Xmg==; gsscw-avito=8BUSxUDREJLWmfrHrm/0btzvvhKLzfwqTscNXuDpPR3odscrZrIeWS9/CkqglRXWfeEFNeTWXWMTdcmnvhVS6FnvjCyGBiCzY/Gsrb030cPbWYvgFfhk1WSp4XADRNd4ZWMfwje3GWP+eFOh2TFWmP7hcN/rphBKaj9bo66Js67fbkp1XOuWMtkL3zIGLWzKw+MTygRs+nb1OQhEPepy0OSjIzOG7fd0PKQAjY8H1/QdyFCFNrtRnOe+wwX5rg==; gsscw-avito=8BUSxUDREJLWmfrHrm/0btzvvhKLzfwqTscNXuDpPR3odscrZrIeWS9/CkqglRXWfeEFNeTWXWMTdcmnvhVS6FnvjCyGBiCzY/Gsrb030cPbWYvgFfhk1WSp4XADRNd4ZWMfwje3GWP+eFOh2TFWmP7hcN/rphBKaj9bo66Js67fbkp1XOuWMtkL3zIGLWzKw+MTygRs+nb1OQhEPepy0OSjIzOG7fd0PKQAjY8H1/QdyFCFNrtRnOe+wwX5rg==; cfidsw-avito=sIF3V/0529sIxYnt6lMfYeH1xBNWANit8qDaQnVvfZrxfrVr2MGIFZB5kjwRpx4OW1FqE0GyEd6SF4+b0DQRRvhLyRRG7ZmQ+Qh5WPSZv/Fbl9RfDrfxX0Omojoxjc9fDKE1kkbY7N+GUQX9yjpON8kRBnoWco4Aa1U/Bg==; fgsscw-avito=Ea7755df6a127af1e6c47a65fd0056f7c42e2811; fgsscw-avito=Ea7755df6a127af1e6c47a65fd0056f7c42e2811; _ym_isad=2; f=5.0c4f4b6d233fb90636b4dd61b04726f147e1eada7172e06c47e1eada7172e06c47e1eada7172e06c47e1eada7172e06cb59320d6eb6303c1b59320d6eb6303c1b59320d6eb6303c147e1eada7172e06c8a38e2c5b3e08b898a38e2c5b3e08b890df103df0c26013a7b0d53c7afc06d0b2ebf3cb6fd35a0ac0df103df0c26013a8b1472fe2f9ba6b9e2bfa4611aac769efa4d7ea84258c63d59c9621b2c0fa58f915ac1de0d034112ad09145d3e31a56946b8ae4e81acb9fae2415097439d4047fb0fb526bb39450a46b8ae4e81acb9fa34d62295fceb188dd99271d186dc1cd03de19da9ed218fe2d50b96489ab264edd50b96489ab264edd50b96489ab264ed46b8ae4e81acb9fa38e6a683f47425a8352c31daf983fa077a7b6c33f74d335cb88de1666d503ec6255f55f36b9873b31d49c1c93fcdfd74c97fa6b2200ff95afc0488193561305817c7721dca45217bb350872d8cb7fbbb7f1988ff29cf017746b8ae4e81acb9fa46b8ae4e81acb9fa02c68186b443a7ac401959c92f93565f1769115734d9269b2da10fb74cac1eab2da10fb74cac1eab25037f810d2d41a8134ecdeb26beb8b53778cee096b7b985bf37df0d1894b088; ft="Tw1+by1lWI7Vsgfum2H+vFwRzM/1ATgWgX/ums7g5IXcPlXbs7U/dg5/k6aourRjbGdOY7OGmewEdmK5IZTtV03IGzNR34/P+z0hbp0DN1Wx74omSCPeVxdECdlwm2Cob+B6+f1M4GgvVhKymbp4Xx1CIO3FDm7bdYPdCC0CXmrzZGWr++5OCU0Pp5FTt0u4"; cto_bundle=ewXK6194VFU1NHREcG5xJTJGYm1hcnBERzA1dEwwaDJKSHI5dzcwRlZDUHppQXlIQThEMm9iUDVUdWMlMkZOZUZudGtjMHFqZGIlMkZweU54bXp0JTJCWTRsNml2ZUxMdjQzZVRhVkFMNE1vRE1pZWVmOXMwdWdqUjA5M3p6M0ZVdG96NFB0UGx4M1BzWEh2UFVISUZHc0pLWVVwU0VYYWYxUjJWanMlMkJrd2I2eGxDd0cyYUc3bHdUSWxSb0laOHRFd3hCZFhNdGtCU3JXVmlvTGlaaGZzc3V1UTdWcCUyRmIxOUpjSEJQNURxNGVXOWw4RjNiZVZZYWh4NW1hNUtGQlFYQWklMkJzUVdjMUFFMks; _ga_WW6Q1STJ8M=GS1.1.1699037156.5.0.1699037160.0.0.0; _ga_ZJDLBTV49B=GS1.1.1699037156.5.0.1699037160.0.0.0; v=1699079141; _ym_visorc=b; SEARCH_HISTORY_IDS=4%2C; luri=nizhniy_novgorod; buyer_location_id=640860; dfp_group=9; _buzz_fpc=JTdCJTIycGF0aCUyMiUzQSUyMiUyRiUyMiUyQyUyMmRvbWFpbiUyMiUzQSUyMi53d3cuYXZpdG8ucnUlMjIlMkMlMjJleHBpcmVzJTIyJTNBJTIyTW9uJTJDJTIwMDQlMjBOb3YlMjAyMDI0JTIwMDclM0EwNyUzQTM3JTIwR01UJTIyJTJDJTIyU2FtZVNpdGUlMjIlM0ElMjJMYXglMjIlMkMlMjJ2YWx1ZSUyMiUzQSUyMiU3QiU1QyUyMnVmcCU1QyUyMiUzQSU1QyUyMjQxZWE5OGQwZmJlYzAxYzE4ZjU0ZTYwNzA3MGMxZDE4JTVDJTIyJTJDJTVDJTIyYnJvd3NlclZlcnNpb24lNUMlMjIlM0ElNUMlMjIxMTkuMCU1QyUyMiU3RCUyMiU3RA==; abp=0; _ga_M29JC28873=GS1.1.1699079145.14.1.1699081684.7.0.0; sx=H4sIAAAAAAAC%2F6STS3brOAxE96KxB%2BAPILIbECCd548ky09ypBztvY8HTsc97Q3cqlO4%2BO4cMDF6cQKRpLIWNG%2FBqXei7Ev38d0t3UdXILmaWqQGMWTnsliuKsGalSYtk0sKytwdutp9OGR2mJDCfuicE64Fg2uh5JiiFG01aWYzzt7lV0RzMDHwiZe0yECfjPFyoc88eOjnZfhNzpDjfui8E1CkUipripCjRp8TG7nmG0v%2BX%2BUJ%2BBlhxD6FkhIxk8taQ%2FSAKBZqc0SviLM%2FKs9treso6VHGcFvndQu9z2V6TNM7mdN%2B6IJQDpx9y%2BhMQShoKFZycdpYXHqRt96W802Py1XcNpYyJhlsjtuKl2v48m%2FkFHE%2FdBG0omdlH6OpLxmsRShckUspJbzIXgI2Zbo9btAqbt5Nk%2BQ%2Fkl1r%2FXh7Hzz4%2FdChi06JqBXRZOhqVvIUs8YYqpMfW5C%2F5nH0VT%2Fp%2FAnGj3mZfOivJ%2Bjv43b%2FTcaYnmsgIqoRNkZOGJErlRrYKIEqGb%2FI62WeeFY%2FHo9h%2Fvvo18vUc70Pf6drfzuf3zv7vB86DdZqqSJsahJqacqxKjEGlhZ%2BOsPVTrfrOX1t96UtAMXuemZdTo9%2B2P78uiDkSPFJNqbYHFhQqVqBOYccvTlG4BjzjxtgcR34caNjGxC30zKhmCA8%2F26w%2F4gdntY1SCq5SCZDTCGlytXVwgEykYr7d41NWgYAG%2FDq%2FRhOC%2FA6DtaKcYJ3Nzjt%2Bz8BAAD%2F%2F6JlbtTxAwAA; tmr_detect=0%7C1699081687388',
    'referer': 'https://www.avito.ru/user/aea431590bda05adb724a8a071d0e0c9/profile/all?src=search_seller_info&sellerId=aea431590bda05adb724a8a071d0e0c9',
    'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': useragent.random}

params = {
    'limit': '25',
    'offset': '25',
    'sortRating': 'date_desc',
    'summary_redesign': '1',
}

options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")

browser = webdriver.Chrome(options=options)

# browser.add_cookie(cookie_dict=cookies)

browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    'source': '''
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
  '''
})
browser.maximize_window()


try:
    browser.get(url=url)
    time.sleep(5)
    src = browser.page_source

except Exception as ex:
    print(ex)

finally:
    browser.close()
    browser.quit()

# res_dict = json.loads(src.lstrip('<html><head><meta name="color-scheme" content="light dark"></head><body><pre style="word-wrap:'
#                  ' break-word; white-space: pre-wrap;">').rstrip('</pre></body></html>'))

soup = BeautifulSoup(src, 'lxml')


json_data = soup.find('pre').text
print(json.loads(json_data))

