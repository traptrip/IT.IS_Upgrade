FROM python:3.6

COPY Pipfile Pipfile.lock ./
RUN pip install pipenv && pipenv install --system

ARG APP_DIR=/simple_analitics_server
WORKDIR "$APP_DIR"

COPY . $APP_DIR/
