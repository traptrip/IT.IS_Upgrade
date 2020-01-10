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

import pandas as pd
import motor.motor_asyncio


class MongoDB:
    def __init__(self, db_name, host, port):
        self.db_name = db_name
        self.uri = os.getenv('DOCKER_MONGO', f"mongodb://{host}:{port}/")
        self.mongo = motor.motor_asyncio.AsyncIOMotorClient(self.uri)
        self.db = self.mongo[db_name]
        self.collection = self.db['logs']

    async def insert_one(self, item):
        if not await self.collection.find_one(item):
            await self.collection.insert_one(item)
            return True
        else:
            return False

    async def get_unique_ips(self):
        return self.collection.distinct("ip")

    async def get_all_actions(self):
        return self.collection.find()

    async def add_country_by_ip(self, ip, country):
        """
        Добавление поля country ко всем строчкам базы данных с определенным ip
        """
        await self.collection.update_many({"ip": ip}, {"$set": {"country": country}})

    async def count_countries(self):
        """
        Посетители из какой страны совершают больше всего действий на сайте?
        Считается суммарное посещеиние сайта за все время
        """
        countries_entry = self.collection.aggregate([{"$group": {"_id": "$country", "count": {"$sum": 1}}}])
        return countries_entry

    async def interest_by_country(self):
        """
        Посетители из какой страны чаще всего интересуются товарами из определенных категорий?
        """
        category_interest = await self.collection.aggregate(
            [{"$group":
                  {"_id": "$category",
                   "name": {{"_id": "$country", "count": {"$sum": 1}}}}
              }])
        return category_interest