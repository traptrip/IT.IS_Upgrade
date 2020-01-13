import datetime as dt

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html


class DashServer:
    def __init__(self, app):
        self.db = app.db
        self.external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']  # подключение стилей
        self.app = dash.Dash(__name__, external_stylesheets=self.external_stylesheets)

    def main(self, db):

        def good_categories_items(db):
            """
            Нахождение всех категорий товаров в базе данных
            """
            good_categories = db.get_unique_categories()
            res = []
            for category in good_categories:
                res.append({'label': category.capitalize().replace('_', ' '), 'value': category})
            return res

        self.app.layout = html.Div(children=[
            # html.H1('АНАЛИТИКА ПО САЙТУ "ВСЕ НА ДНО!"'),
            # html.H2('Выполнил: Андрей Попов'),

            dcc.Dropdown(
                id='menu',
                options=[
                    {'label': 'Посетители из каких стран совершают больше всего действий на сайте '
                              '(unknown - список не распознанных стран)',
                     'value': 'top_countries'},

                    {'label': 'Посетители из какой страны чаще всего интересуются товарами из определенных категорий?',
                     'value': 'top_countries_in_category'},

                    {'label': 'В какое время суток чаще всего просматривают определенную категорию товаров?',
                     'value': 'category_interest'},

                    {'label': 'Нагрузка на сайт', 'value': 'site_load'},
                    {'label': 'Количество неоплаченных корзин за определенный период', 'value': 'unpaid_carts'},
                    # {'label': 'Количество повторных покупок', 'value': 'repeated_purchases'},
                ],
                value='top_countries',
                placeholder='Выберете интересующую информацию...'
            ),

            dcc.Dropdown(id='good_categories',
                         options=good_categories_items(self.db),
                         style={'display': 'block'},
                         placeholder='Выберете интересующую категорию...'
                         ),

            dcc.DatePickerSingle(
                id='date_picker',
                min_date_allowed=dt.date.fromisoformat(self.db.get_min_date()),
                max_date_allowed=dt.date.fromisoformat(self.db.get_max_date()),
                display_format="YYYY-MM-DD",
                style={'display': 'block'},
                placeholder="Начальная дата"
            ),

            dcc.DatePickerSingle(
                id='date_picker_range',
                min_date_allowed=dt.date.fromisoformat(self.db.get_min_date()),
                max_date_allowed=dt.date.fromisoformat(self.db.get_max_date()),
                display_format="YYYY-MM-DD",
                style={'display': 'block'},
                placeholder="Конечная дата"
            ),

            html.Button('Обновить информацию', id='button'),

            dcc.Graph(
                id='graph',
                style={'display': 'block'}
            ),

            html.Div(
                id='msg',
                children='',
                style={'display': 'block'}
            )
        ])

        # Функция отслеживающая запрос из меню
        @self.app.callback(
            [Output(component_id='good_categories', component_property='style'),
             Output(component_id='date_picker', component_property='style'),
             Output(component_id='date_picker_range', component_property='style'),
             Output(component_id='graph', component_property='style'),
             Output(component_id='msg', component_property='style')
             ],
            [Input(component_id='menu', component_property='value')])
        def output_format(menu_value):
            """
            menu_value - параметр, который приходит из меню
            out_format - список определяющий, какие элементы будут отрисованы на странице
                0 - не отрисовывать элемент
                1 - отрисовывать
                out_format[0] - good_categories
                out_format[1] - date_picker
                out_format[2] - date_picker_range
                out_format[3] - graph
                out_format[4] - msg
            """
            out_format = [0]*5

            if menu_value == 'top_countries':
                out_format[3] = 1
            elif menu_value == 'top_countries_in_category':
                out_format[0] = 1
                out_format[3] = 1
            elif menu_value == 'category_interest':
                out_format[0] = 1
                out_format[3] = 1
            elif menu_value == 'site_load':
                out_format[1] = 1
                out_format[3] = 1
            elif menu_value == 'unpaid_carts':
                out_format[1] = 1
                out_format[2] = 1
                out_format[4] = 1
            return [{'display': 'block'} if i else {'display': 'none'} for i in out_format]

        @self.app.callback(
            [Output(component_id='graph', component_property='figure'),
             Output(component_id='msg', component_property='children')],
            [Input(component_id='button', component_property='n_clicks')],
            [State(component_id='menu', component_property='value'),
             State(component_id='good_categories', component_property='value'),
             State(component_id='date_picker', component_property='date'),
             State(component_id='date_picker_range', component_property='date')
             ])
        def show_graph(n_clicks, menu_value, category_value, date_value, end_date_value):

            figure = {}
            msg = ''

            def get_countries_entries(countries_entry, countries_num):
                countries_entry = sorted(list(countries_entry), key=lambda x: x['count'])[-countries_num:]
                countries = []
                entries = []
                for d in countries_entry:
                    countries.append(d['_id'])
                    entries.append(d['count'])
                return countries, entries

            if menu_value == 'top_countries':
                countries_entry = db.count_countries()
                countries_num = 10
                countries, entries = get_countries_entries(countries_entry, countries_num)
                figure = {
                    'data': [{
                            'x': countries,
                            'y': entries,
                            'type': 'bar',
                            'name': 'Суммарное число запросов от указанной страны'
                    }],
                    'layout': {
                        'title': '10 cтран с самым большим количеством запросов на сайте',
                        'showlegend': True,
                        'legend': {
                            'x': 0,
                            'y': 1
                        },
                    },
                }

            elif menu_value == 'top_countries_in_category':
                countries_entry = db.interest_by_country(category_value)
                countries_num = 10
                countries, entries = get_countries_entries(countries_entry, countries_num)
                figure = {
                     'data': [{
                         'x': countries,
                         'y': entries,
                         'type': 'bar',
                         'name': 'Суммарное число просмотров от указанной страны'
                     }],
                     'layout': {
                         'title':
                             f'10 стран с самым большим количеством просмотров товаров категории '
                             f'\"{category_value.capitalize().replace("_", " ")}\"',
                         'showlegend': True,
                         'legend': {
                             'x': 0,
                             'y': 1
                         }
                     }
                }

            elif menu_value == 'category_interest':
                categories_entries = db.interest_by_time(category_value)
                timestamps_num = 24
                figure = {
                     'data': [{
                         'x': [dt.datetime(2000, 1, 1, i, 0, 0).time() for i in range(timestamps_num)],
                         'y': categories_entries,
                         'type': 'bar',
                         'name': 'Суммарное число просмотров в указанный час'
                     }],
                     'layout': {
                         'title':
                             f'Суммарное число просмотров товаров категории '
                             f'\"{category_value.capitalize().replace("_", " ")}\" '
                             f'в указанный час',
                     }
                }

            elif menu_value == 'site_load':
                entries = db.get_site_load(date_value)
                timestamps_num = 24
                figure = {
                     'data': [{
                         'x': [dt.datetime(2000, 1, 1, i, 0, 0).time() for i in range(timestamps_num)],
                         'y': entries,
                         'type': 'bar',
                         'name': 'Суммарное число просмотров в указанный час'
                     }],
                     'layout': {
                         'title':
                             f'Нагрузка на сайт в определенную дату',
                     }
                }

            elif menu_value == 'unpaid_carts':
                msg = db.count_unpaid_carts(date_value, end_date_value)

            return figure, msg

    def run(self, host, port):
        self.main(self.db)
        self.app.run_server(host=host, port=port)
