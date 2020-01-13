FROM python:3.7

COPY requirements.txt ./
RUN pip install -r requirements.txt

ARG APP_DIR=/simple_analitics_server
WORKDIR "$APP_DIR"

COPY . $APP_DIR/
