FROM python:3.11.7-slim

WORKDIR /usr/src/api

ENV PYTHONPATH=/usr/src/api

COPY requirements.txt .

RUN apt-get update && pip install --upgrade pip && pip install -r requirements.txt  

COPY . .