FROM python:3

ARG AGGR_TYPE=conf
LABEL maintainer="Kazuki Yokoyama (kmyokoyama@inf.ufrgs.br)"

ENV AGGR_TYPE      ${AGGR_TYPE}

ADD . /usr/src/mconf-aggr/

RUN chmod 744 /usr/src/mconf-aggr/start.sh

RUN pip install -r /usr/src/mconf-aggr/requirements.txt

WORKDIR /usr/src/mconf-aggr/

CMD ["./start.sh", "-c", "/usr/src/mconf-aggr/config/config.json"]
