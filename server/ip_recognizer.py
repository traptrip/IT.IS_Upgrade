import os
import json

from tqdm import tqdm

from ip2geotools.databases.noncommercial import DbIpCity


def recognize_ips_countries(db):
    """
    Создается .json файл, в котором хранятся уникальные ip и их пренадлежность той или иной стране
    Подключение к базе ip адресов происходит с помощью библиотеки ip2geotools
    Формирование .json файла происходит не быстро, поэтому к проекту прилогается полученный ранее файл
    """
    countries = {}
    unique_ips = db.get_unique_ips()  # получение уникальный ip адресов из бд
    for ip in tqdm(unique_ips):
        try:
            response = DbIpCity.get(ip, api_key='free').country
        except:  # если данный ip отсутствует в базе адресов
            response = 'unknown'  # то оставляем значение равным None
        countries[ip] = response

    filename = './database/ip_countries.json'
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            json.dump(countries, f)


def add_ip_countries2db(db):
    filename = './database/ip_countries.json'
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            countries = json.load(f)
    for ip, country in tqdm(countries.items()):
        db.add_country_by_ip(ip, country)
