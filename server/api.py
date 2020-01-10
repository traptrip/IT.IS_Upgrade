import asyncio

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd
from pymongo import MongoClient
from database.mongo import MongoDB


def read_mongo(host='localhost', port=27017):
    def _connect_mongo(host, port):
        conn = MongoClient(host, port)
        return conn['logs']

    db = _connect_mongo(host=host, port=port)
    cursor = db['logs'].find()
    df = pd.DataFrame(list(cursor))
    del df['_id']
    return df


def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )


class DashServer:
    def __init__(self, app):
        self.db = app.db
        self.external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']  # подключение стилей
        self.app = dash.Dash(__name__, external_stylesheets=self.external_stylesheets)

    def main(self, db):
        self.app.layout = html.Div(children=[
            html.H1('АНАЛИТИКА ПО САЙТУ "ВСЕ НА ДНО!"'),
            html.H2('Выполнил: Андрей Попов'),

            dcc.Dropdown(
                id='menu',
                options=[
                    {'label': 'Посетители из каких стран совершают больше всего действий на сайте '
                              '(unknown - список не распознанных стран)',
                     'value': 'top_countries'},
                    # {'label': 'Посетители из какой страны чаще всего интересуются товарами из определенных категорий?',
                    #  'value': 'top_countries_in_category'},
                    # {'label': 'Таблица с данными о действиях покупателей', 'value': 'all_actions'},
                    # {'label': 'Нагрузка на сайт', 'value': 'site_load'},
                    # {'label': 'Количество повторных покупок', 'value': 'repeated_purchases'},
                    # {'label': 'Количество неоплаченных корзин', 'value': 'abandoned_carts'},
                    # {'label': 'Интерес к категории товаров', 'value': 'activity_time'},
                ],
                value='load'
            ),

            html.Div(id='extra_container'),

            html.Div(id='main_container')
        ])

        # Функция отслеживающая запрос из меню
        @self.app.callback(
            Output(component_id='main_container', component_property='children'),
            [Input(component_id='menu', component_property='value')])
        def main_update(value):
            # Уловие для определения того, что выбрал пользователь
            if value == 'top_countries':
                countries_entry = db.count_countries()
                countries_entry = sorted(list(countries_entry), key=lambda x: x['count'])[-10:]
                countries = []
                entries = []
                for d in countries_entry:
                    countries.append(d['_id'])
                    entries.append(d['count'])
                graph = dcc.Graph(
                    id='graph',
                    style={'display': 'block'},
                    figure={
                        'data': [
                            {
                                'x': countries,
                                'y': entries,
                                'type': 'bar',
                                'name': 'Число запросов от указанной страны'
                            }
                        ],
                        'layout': {
                            'title': '10 cтран с самым большим количеством запросов на сайте',
                            'showlegend': True,
                            'legend': {
                                'x': 0,
                                'y': 1
                            }
                        },
                    },
                )
                return graph

            elif value == '':
                pass

    def run(self, host, port):
        self.main(self.db)
        self.app.run_server(host=host, port=port)
