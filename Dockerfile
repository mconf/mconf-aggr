FROM python:3.6-alpine AS base

FROM base AS builder

RUN mkdir /install

WORKDIR /install

COPY ./requirements.txt /requirements.txt

RUN apk update && \
    apk add postgresql-libs && \
    apk add --virtual .build-deps gcc musl-dev postgresql-dev

RUN pip install --install-option="--prefix=/install" -r /requirements.txt

RUN apk --purge del .build-deps

FROM base

RUN apk update && apk add postgresql-libs libpq

COPY --from=builder /install /usr/local

COPY ./config/default.json /usr/src/mconf-aggr/config/default.json
COPY ./mconf_aggr/__init__.py /usr/src/mconf-aggr/mconf_aggr/__init__.py
COPY ./mconf_aggr/aggregator/ /usr/src/mconf-aggr/mconf_aggr/aggregator/
COPY ./mconf_aggr/webhook/ /usr/src/mconf-aggr/mconf_aggr/webhook/
COPY ./main.py /usr/src/mconf-aggr/main.py

WORKDIR /usr/src/mconf-aggr/

COPY ./config/config_webhook.json.tmpl ./config/config_webhook.json.tmpl

RUN apk add --no-cache openssl

ENV DOCKERIZE_VERSION v0.6.1

RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
&& tar -C /usr/local/bin -xzvf dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
&& rm dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz

CMD dockerize -template ./config/config.json.tmpl:./config/config.json gunicorn main:app --bind=0.0.0.0:8000