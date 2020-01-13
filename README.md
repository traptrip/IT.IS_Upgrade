# IT.IS_Upgrade
 Тестовое задание на курс IT.IS-Upgrade
# Как запустить приложение
### Через Docker
  1) Иметь на компьютере предустановленный docker и docker-compose 
  (https://docs.docker.com/install/, https://docs.docker.com/compose/install/)
  2) В папке с проектом ввести команду (приложение сгенерирует базу данных и запустит веб сервер)
  > docker-compose up --build

### Альтернативный способ
  1) установить и запустить mongodb (https://docs.mongodb.com/v4.0/installation/)
  2) в папке с проектом 
  > pip install -r requirements.txt

  > invoke create-database start-dash-app
