FROM python:3.9.10-alpine AS base

FROM base AS builder

RUN mkdir /install

WORKDIR /install

COPY ./requirements.txt /requirements.txt

RUN apk update && \
    apk add postgresql-libs && \
    apk add --virtual .build-deps gcc musl-dev postgresql-dev

RUN pip install --prefix=/install -r /requirements.txt

RUN apk --purge del .build-deps

FROM base

RUN apk update && apk add postgresql-libs libpq
RUN apk add --no-cache openssl

COPY --from=builder /install /usr/local

COPY ./mconf_aggr/__init__.py /usr/src/mconf-aggr/mconf_aggr/__init__.py
COPY ./mconf_aggr/aggregator/ /usr/src/mconf-aggr/mconf_aggr/aggregator/
COPY ./mconf_aggr/webhook/ /usr/src/mconf-aggr/mconf_aggr/webhook/
COPY ./mconf_aggr/logging.json /usr/src/mconf-aggr/mconf_aggr/logging.json
COPY ./main.py /usr/src/mconf-aggr/main.py

WORKDIR /usr/src/mconf-aggr/


CMD gunicorn main:app --bind=0.0.0.0:8000 --worker-class gevent
