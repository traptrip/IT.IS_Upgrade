from server.ip_recognizer import add_ip_countries2db


def logs2database(db, log_file):
    """
    По файлу с логами формирует базу данных mongodb
    """
    with open(log_file, 'r') as file:
        logs = file.read().split(sep='\n')

    all_data = []
    for log in logs:
        if len(log) == 0:  # исключоет пустые строки в логах
            continue

        log = log.split()  # разбиение логов по пробелам
        data = dict()
        data['date'] = log[2]
        data['time'] = log[3]
        data['ip'] = log[-2]
        url = log[-1]
        if '?' not in url and 'success' not in url:
            data['action_type'] = 'page'
            res = url.split('/')  # разбиение url по слэшам
            if len(res) > 5:
                data['good_category'] = res[-3]
                data['good_name'] = res[-2]
            elif len(res) == 5:
                data['good_category'] = res[-2]
            else:
                data['url'] = url
        elif 'cart?' in url:
            data['action_type'] = 'cart'
            res = url.split('=')  # разбиение url по "="
            data['cart_id'] = res[-1]
            data['good_id'] = res[-3].split('&')[0]
            data['amount'] = res[-2].split('&')[0]
        elif 'pay?' in url:
            data['action_type'] = 'pay'
            res = url.split('=')  # разбиение url по "="
            data['user_id'] = res[-2].split('&')[0]
            data['cart_id'] = res[-1]
        elif 'success_pay' in url:
            data['action_type'] = 'success_pay'
            # разбиение url по "_", взятие последнего эл-та и исключение из него последнего слэша
            res = url.split('_')[-1][:-1]
            data['cart_id'] = res
        all_data.append(data)  # добавление текущей строки к остальным данным
    db.collection.insert_many(all_data)
    add_ip_countries2db(db)  # добавление информации о регионе из которого совершено действие на сайте
