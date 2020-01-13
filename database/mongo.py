"""
СТРУКТУРА БД:
datetime , ip , action_type , page        , good_category , good_name
                              cart        , cart_id       , good_id   , amount
                              pay         , user_id       , cart_id
                              success_pay , cart_id


Поле action_type может быть 4-ех видов, в зависимости от которых строятся остальные поля

'page' - переход по станицам с товарами
    good_category - категория товара
    good_name     - наименование товара
    url(заполняется, только если пользователь на гглавной странице) - ссылка на страницу

'cart' - добавление товара в корзину
    cart_id - id корзины
    good_id - id товара
    amount  - кол-во товара

'pay' - страница с оплатой
    user_id - id пользователя
    cart_id - id корзины

'success_pay' - страница, подтверждающая успешную оплату
    cart_id - id корзины
"""
import os
import datetime as dt

from pymongo import MongoClient


class MongoDB:
    def __init__(self, db_name, host, port):
        self.url = os.getenv('DOCKER_MONGO', f"mongodb://{host}:{port}/")
        self.mongo = MongoClient(self.url)
        self.db = self.mongo[db_name]
        self.collection = self.db['logs']

    def get_all_actions(self):
        """
        :return: все записи в базе данных
        """
        return self.collection.find()

    def get_unique_ips(self):
        """
        :return: все уникальные ip адреса в базе данных
        """
        return self.collection.distinct("ip")

    def get_unique_categories(self):
        """
        :return: все уникальные названия категорий товаров в базе данных
        """
        return self.collection.distinct("good_category")

    def add_country_by_ip(self, ip, country):
        """
        Добавление поля country ко всем строчкам базы данных с определенным ip
        """
        self.collection.update_many({"ip": ip}, {"$set": {"country": country}})

    def count_countries(self):
        """
        Посетители из какой страны совершают больше всего действий на сайте?
        Считается суммарное посещеиние сайта за все время
        """
        countries_entry = self.collection.aggregate([{"$group": {"_id": "$country", "count": {"$sum": 1}}}])
        return countries_entry

    def interest_by_country(self, category_name):
        """
        Посетители из какой страны чаще всего интересуются товарами из определенных категорий?
        """
        category_interest = self.collection\
            .aggregate([{"$match": {"good_category": category_name}},
                        {"$group": {"_id": "$country", "count": {"$sum": 1}}}])
        return category_interest

    def interest_by_time(self, category_name):
        """
        Распределение просмотров данной категории по времени
        """
        category_interest = self.collection.find({"good_category": category_name})
        res = [0] * 24
        for i in category_interest:
            res[dt.time.fromisoformat(i['time']).hour] += 1
        return res

    def get_min_date(self):
        """
        Получение начальной даты находящихся в базе данных
        """
        min_date = self.collection.find_one(sort=[("date", 1)])["date"]
        return min_date

    def get_max_date(self):
        """
        Получение конечной даты находящихся в базе данных
        """
        max_date = self.collection.find_one(sort=[("date", -1)])["date"]
        return max_date

    def get_site_load(self, date):
        """
        Получение почасовой нагрузки на сайт в определенную дату (date)
        """
        timestamps = self.collection.find({"date": date}, {"time": 1})
        res = [0]*24
        for i in timestamps:
            res[dt.time.fromisoformat(i["time"]).hour] += 1
        return res

    def count_unpaid_carts(self, start_date, end_date):
        """
        :return: кол-во неоплаченных корзин с даты start по дату end
        """
        carts = self.collection\
            .find({'date': {'$gte': start_date, '$lte': end_date}, 'action_type': 'cart'})\
            .distinct("cart_id")
        pays = self.collection.find({'date': {'$gte': start_date, '$lte': end_date}, 'action_type': 'success_pay'}).count()
        return len(carts)-pays
