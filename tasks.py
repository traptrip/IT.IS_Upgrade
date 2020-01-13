"""
Запуск приложений (порядок запуска соблюдён)

1. create_database            -  приложение для формирования базы данных
2. discover_countries_by_ips  -  приложение для формирования файла с ip адресами и странами, которым они принадлежат
3. start_dash_app             -  веб приложение для аналитики
"""


from invoke import task


@task
def start_dash_app(ctx):
    """
    Запуск веб приложения с аналитикой
    """
    from app import DashApp
    dash_worker = DashApp(ctx.config)
    dash_worker.run()


@task
def create_database(ctx):
    """
    Создание базы данных по логам
    """
    from app import DatabaseCreator
    creator = DatabaseCreator(ctx.config)
    creator.create_database()


@task
def discover_countries_by_ips(ctx):
    """
    Формирование .json файла с ip адресами и странами, которым они принадлежат
    Используется библиотека ip2geotools
    """
    from app import IpRecognizer
    creator = IpRecognizer(ctx.config)
    creator.run()
