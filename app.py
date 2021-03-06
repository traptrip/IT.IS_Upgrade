from database.mongo import MongoDB
from database.logs2database import logs2database
from server.ip_recognizer import recognize_ips_countries
from server.api import DashServer


class DashApp:
    """
    Приложение для аналитики по данным, хранящимся в базе данных
    """
    def __init__(self, config):
        self.config = config
        self.db = MongoDB(config.mongo.db, config.mongo.url, config.mongo.port)

        self.host = config.api.host
        self.port = config.api.port
        self.web_server = DashServer(self)

    def run(self):
        self.web_server.run(host=self.host, port=self.port)


class DatabaseCreator:
    """
    Генератор базы данных из файла с логами
    """
    def __init__(self, config):
        self.config = config
        self.db = MongoDB(config.mongo.db, config.mongo.url, config.mongo.port)
        self.log_file = config.logs.log_file

    def create_database(self):
        logs2database(self.db, self.log_file)


class IpRecognizer:
    """
    Генератор .json файла, в котором хранятся уникальные ip и их пренадлежность той или иной стране
    """
    def __init__(self, config):
        self.config = config
        self.db = MongoDB(config.mongo.db, config.mongo.url, config.mongo.port)

    def run(self):
        recognize_ips_countries(self.db)
