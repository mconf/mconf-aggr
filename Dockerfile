FROM python:3

LABEL maintainer="Kazuki Yokoyama (kmyokoyama@inf.ufrgs.br)"

ADD . /mconf-aggr/

RUN pip install -r /mconf-aggr/requirements.txt

WORKDIR /mconf-aggr/

CMD ["python", "main.py"]
