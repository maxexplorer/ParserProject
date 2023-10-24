from datetime import datetime
import os

import requests
from pandas import DataFrame, ExcelWriter
import openpyxl

start_time = datetime.now()

locations = [

    '222',
    '223',
    '225',
    '224',
    '227',
    '228',
    '226',
    '229',

]


def get_data(locations):
    headers = {
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Origin': 'https://www.bayut.com',
        'Referer': 'https://www.bayut.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML like Gecko) '
                      'Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931',
        'accept': 'application/json',
        'content-type': 'application/x-www-form-urlencoded',
        'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    result_list = []

    for i in locations:
        data = f'{{"requests":[{{"indexName":"bayut-production-agencies-ads-count-desc-en","params":"page=0&hitsPerPage=12&query=&optionalWords=&facets=%5B%5D&maxValuesPerFacet=10&attributesToHighlight=%5B%5D&attributesToRetrieve=%5B%22name%22%2C%22logo%22%2C%22agentsCount%22%2C%22locations%22%2C%22stats%22%2C%22user_langs%22%2C%22specialities%22%2C%22user_image_id%22%2C%22about_user%22%2C%22rent_count%22%2C%22sale_count%22%2C%22agency%22%2C%22service_areas%22%2C%22isTruBroker%22%2C%22agency%22%2C%22area%22%2C%22baths%22%2C%22category%22%2C%22contactName%22%2C%22externalID%22%2C%22id%22%2C%22location%22%2C%22objectID%22%2C%22phoneNumber%22%2C%22coverPhoto%22%2C%22photoCount%22%2C%22price%22%2C%22product%22%2C%22productLabel%22%2C%22purpose%22%2C%22geography%22%2C%22permitNumber%22%2C%22referenceNumber%22%2C%22rentFrequency%22%2C%22rooms%22%2C%22slug%22%2C%22slug_l1%22%2C%22slug_l2%22%2C%22title%22%2C%22title_l1%22%2C%22title_l2%22%2C%22createdAt%22%2C%22updatedAt%22%2C%22ownerID%22%2C%22isVerified%22%2C%22propertyTour%22%2C%22verification%22%2C%22completionStatus%22%2C%22furnishingStatus%22%2C%22-agency.tier%22%2C%22requiresLogin%22%2C%22coverVideo%22%2C%22videoCount%22%2C%22description%22%2C%22description_l1%22%2C%22description_l2%22%2C%22floorPlanID%22%2C%22panoramaCount%22%2C%22hasMatchingFloorPlans%22%2C%22hasTransactionHistory%22%2C%22state%22%2C%22photoIDs%22%2C%22reactivatedAt%22%2C%22hidePrice%22%2C%22extraFields%22%2C%22projectNumber%22%2C%22locationPurposeTier%22%2C%22ownerAgent%22%2C%22hasEmail%22%5D&filters=(stats.locationsWithAds%3A%{i}%22)&numericFilters=stats.adsCount%3E%3D1"}}]}}'

        try:
            response = requests.post(
                'https://ll8iz711cs-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(3.35.1)'
                '%3B%20Browser%20(lite)&x-algolia-application-id=LL8IZ711CS&x-algolia-api-key=802406b04be9b83e3a59dbb7e61e2778',
                headers=headers,
                data=data,
            )
            dict_data = response.json()
            count_pages = int(dict_data['results'][0]['nbPages'])
        except Exception as ex:
            print(f'{i} - {ex}')
            continue

        for j in range(count_pages):
            data = f'{{"requests":[{{"indexName":"bayut-production-agencies-ads-count-desc-en","params":"page={j}&hitsPerPage=12&query=&optionalWords=&facets=%5B%5D&maxValuesPerFacet=10&attributesToHighlight=%5B%5D&attributesToRetrieve=%5B%22name%22%2C%22logo%22%2C%22agentsCount%22%2C%22locations%22%2C%22stats%22%2C%22user_langs%22%2C%22specialities%22%2C%22user_image_id%22%2C%22about_user%22%2C%22rent_count%22%2C%22sale_count%22%2C%22agency%22%2C%22service_areas%22%2C%22isTruBroker%22%2C%22agency%22%2C%22area%22%2C%22baths%22%2C%22category%22%2C%22contactName%22%2C%22externalID%22%2C%22id%22%2C%22location%22%2C%22objectID%22%2C%22phoneNumber%22%2C%22coverPhoto%22%2C%22photoCount%22%2C%22price%22%2C%22product%22%2C%22productLabel%22%2C%22purpose%22%2C%22geography%22%2C%22permitNumber%22%2C%22referenceNumber%22%2C%22rentFrequency%22%2C%22rooms%22%2C%22slug%22%2C%22slug_l1%22%2C%22slug_l2%22%2C%22title%22%2C%22title_l1%22%2C%22title_l2%22%2C%22createdAt%22%2C%22updatedAt%22%2C%22ownerID%22%2C%22isVerified%22%2C%22propertyTour%22%2C%22verification%22%2C%22completionStatus%22%2C%22furnishingStatus%22%2C%22-agency.tier%22%2C%22requiresLogin%22%2C%22coverVideo%22%2C%22videoCount%22%2C%22description%22%2C%22description_l1%22%2C%22description_l2%22%2C%22floorPlanID%22%2C%22panoramaCount%22%2C%22hasMatchingFloorPlans%22%2C%22hasTransactionHistory%22%2C%22state%22%2C%22photoIDs%22%2C%22reactivatedAt%22%2C%22hidePrice%22%2C%22extraFields%22%2C%22projectNumber%22%2C%22locationPurposeTier%22%2C%22ownerAgent%22%2C%22hasEmail%22%5D&filters=(stats.locationsWithAds%3A%{i}%22)&numericFilters=stats.adsCount%3E%3D1"}}]}}'

            try:
                response = requests.post(
                    'https://ll8iz711cs-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(3.35.1)'
                    '%3B%20Browser%20(lite)&x-algolia-application-id=LL8IZ711CS&x-algolia-api-key=802406b04be9b83e3a59dbb7e61e2778',
                    headers=headers,
                    data=data,
                )
                dict_data = response.json()
                items = dict_data['results'][0]['hits']
            except Exception as ex:
                print(f'{i}/{j} - {ex}')
                continue

            for item in items:
                location = item.get('location')
                name = item.get('name')
                properties_count = item.get('stats').get('adsCount')
                sale_count = item.get('stats').get('adsSaleCount')
                rent_count = item.get('stats').get('adsRentCount')
                property_types = ', '.join(item.get('stats').get('categoryTypes'))
                service_areas = ', '.join(item.get('stats').get('serviceAreas'))
                phone_number = item.get('phoneNumber').get('phone')
                mobile_number = item.get('phoneNumber').get('mobile')
                proxy_number = item.get('phoneNumber').get('proxyPhone')

                result_list.append(
                    {
                        'City': location,
                        'Name': name,
                        'Properties': properties_count,
                        'For Sale': sale_count,
                        'For Ren': rent_count,
                        'Property Types': property_types,
                        'Service Areas': service_areas,
                        'Phone number': phone_number,
                        'Mobile number': mobile_number,
                        'Proxy number': proxy_number
                    }
                )
                print(f'{location} - {name}')

    return result_list


def save_excel(data):
    if not os.path.exists('data'):
        os.mkdir('data')

    dataframe = DataFrame(data)

    with ExcelWriter('data/data.xlsx', mode='w') as writer:
        dataframe.to_excel(writer, sheet_name='data')

    print(f'Данные сохранены в файл "data.xlsx"')


def main():
    data = get_data(locations=locations)
    save_excel(data)
    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
