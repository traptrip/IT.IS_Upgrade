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

from pymongo import MongoClient


class MongoDB:
    def __init__(self, db_name, host, port):
        self.url = os.getenv('DOCKER_MONGO', f"mongodb://{host}:{port}/")
        self.mongo = MongoClient(self.url)
        self.db = self.mongo[db_name]
        self.collection = self.db['logs']

    def insert_one(self, item):
        if not self.collection.find_one(item):
            self.collection.insert_one(item)
            return True
        else:
            return False

    def get_unique_ips(self):
        return self.collection.distinct("ip")

    def get_all_actions(self):
        return self.collection.find()

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

    def interest_by_country(self):
        """
        Посетители из какой страны чаще всего интересуются товарами из определенных категорий?
        """
        category_interest = self.collection.aggregate(
            [{"$group":
                  {"_id": "$category",
                   "name": {{"_id": "$country", "count": {"$sum": 1}}}}
              }])
        return category_interest


