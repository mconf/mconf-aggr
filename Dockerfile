FROM python:3

LABEL maintainer="Kazuki Yokoyama (kmyokoyama@inf.ufrgs.br)"

ADD . /usr/src/mconf-aggr/

RUN pip install -r /usr/src/mconf-aggr/requirements.txt

WORKDIR /usr/src/mconf-aggr/

CMD ["python", "main.py", "-c", "/usr/src/mconf-aggr/config/config.json"]
