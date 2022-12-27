# syntax=docker/dockerfile:1

FROM python:slim-buster

RUN apt-get -y -qq update && \
    apt-get -y -qq install curl cron

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install -e .

ENV PORT 8000
EXPOSE $PORT

CMD gunicorn lifx_night_light.app:app --bind 0.0.0.0:$PORT
