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


# df = read_mongo()
#
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']  # подключение стилей
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#
# # Формирование HTML страницы
# app.layout = html.Div(children=[
#     html.H1('АНАЛИТИКА ПО САЙТУ "ВСЕ НА ДНО!"'),
#     html.H2('Выполнил: Андрей Попов'),
#
#     dcc.RadioItems(
#         id='menu',
#         options=[
#             {'label': 'Таблица с данными о действиях покупателей', 'value': 'all_actions'},
#             {'label': 'Нагрузка на сайт', 'value': 'site_load'},
#             {'label': 'Количество повторных покупок', 'value': 'repeated_purchases'},
#             {'label': 'Количество неоплаченных корзин', 'value': 'abandoned_carts'},
#             {'label': 'Интерес к категории товаров', 'value': 'activity_time'},
#         ],
#         value='load'
#     ),
#
#     generate_table(df)
# ])
#
# if __name__ == '__main__':
#     app.run_server(debug=True)

# app.layout = html.Div([
#     html.H1('АНАЛИТИКА ПО САЙТУ "ВСЕ НА ДНО!"'),
#     html.H2('Выполнил: Андрей Попов'),
#
#     html.Div(id='amount-per-week')
# ])
#
# app.layout = html.Div(children=[
#     html.H1(children='Hello Dash'),
#
#     html.Div(children='''
#         Dash: A web application framework for Python.
#     '''),
#
#     dcc.Graph(
#         id='example-graph',
#         figure={
#             'data': [
#                 {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
#                 {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
#             ],
#             'layout': {
#                 'title': 'Dash Data Visualization'
#             }
#         }
#     )
# ])
#
# if __name__ == '__main__':
#     app.run_server(debug=True)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']  # подключение стилей
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


# class DashServer:
#     def __init__(self, app):
#         db = app.db
#
#     @staticmethod
#     def make_html():
#         app.layout = html.Div(children=[
#             html.H1('АНАЛИТИКА ПО САЙТУ "ВСЕ НА ДНО!"'),
#             html.H2('Выполнил: Андрей Попов'),
#
#             dcc.RadioItems(
#                 id='menu',
#                 options=[
#                     {'label': 'Посетители из какой страны совершают больше всего действий на сайте',
#                      'value': 'top_countries'},
#                     {'label': 'Таблица с данными о действиях покупателей', 'value': 'all_actions'},
#                     {'label': 'Нагрузка на сайт', 'value': 'site_load'},
#                     {'label': 'Количество повторных покупок', 'value': 'repeated_purchases'},
#                     {'label': 'Количество неоплаченных корзин', 'value': 'abandoned_carts'},
#                     {'label': 'Интерес к категории товаров', 'value': 'activity_time'},
#                 ],
#                 value='load'
#             ),
#             html.Div(id='MainOutputContainer')
#
#         ])
#
#         # Функция отслеживающая запрос из меню
#         @app.callback(
#             Output('MainOutputContainer', 'children'),
#             [Input('menu', 'value')])
#         def main_update(value):
#             # Уловие для определения, что выбрал пользователь
#             if value == 'top_countries':
#                 countries_entry = db.count_countries()
#                 return html.H5(countries_entry)
#
#     def run(self, host, port):
#         self.make_html()
#         app.run_server(host=host, port=port)


db = MongoDB('logs', '0.0.0.0', '27017')
loop = asyncio.get_event_loop()

app.layout = html.Div(children=[
    html.H1('АНАЛИТИКА ПО САЙТУ "ВСЕ НА ДНО!"'),
    html.H2('Выполнил: Андрей Попов'),

    dcc.Dropdown(
        id='menu',
        options=[
            {'label': 'Посетители из каких стран совершают больше всего действий на сайте (None - страна неизвестна)',
             'value': 'top_countries'},
            # {'label': 'Таблица с данными о действиях покупателей', 'value': 'all_actions'},
            # {'label': 'Нагрузка на сайт', 'value': 'site_load'},
            # {'label': 'Количество повторных покупок', 'value': 'repeated_purchases'},
            # {'label': 'Количество неоплаченных корзин', 'value': 'abandoned_carts'},
            # {'label': 'Интерес к категории товаров', 'value': 'activity_time'},
        ],
        value='load'
    ),

    html.Div(id='out_container')
])


# Функция отслеживающая запрос из меню
@app.callback(
    Output(component_id='out_container', component_property='children'),
    [Input(component_id='menu', component_property='value')])
def main_update(value):
    # Уловие для определения, что выбрал пользователь
    if value == 'top_countries':
        countries_entry = db.count_countries()
        countries_entry = list(countries_entry)
        countries = []
        entries = []
        for d in countries_entry:
            countries.append(d['_id'])
            entries.append(d['count'])

        print(countries_entry)

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
                    'title': 'Нагрузка на сайт',
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


app.run_server()
