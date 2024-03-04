FROM python:3.11.7-slim

RUN addgroup --gid 10001 apiuser && \
    adduser --uid 10001 --gid 10001 --disabled-password --gecos "" apiuser

WORKDIR /usr/src/auth-service

ENV PYTHONPATH=/usr/src/auth-service

COPY /requirements/base.txt /requirements/

RUN apt-get update && \
    pip install --upgrade pip && \
    pip install -r /requirements/base.txt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY --chown=apiuser:apiuser . .

USER apiuser