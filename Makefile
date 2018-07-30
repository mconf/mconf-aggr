CONFIG_PATH=~/config.json
AGGR_PATH=$(shell pwd)
TAG=latest

run-webhook:
	@python main_webhook.py -c $(CONFIG_PATH)

run-zabbix:
	@python main_zabbix.py -c $(CONFIG_PATH)

docker-build-webhook:
	docker build -f Dockerfile.webhook -t mconf-aggr-webhook:$(TAG) .

docker-build-zabbix:
	docker build -f Dockerfile.zabbix -t mconf-aggr-zabbix:$(TAG) .

docker-run-webhook:
	docker run --rm -v $(CONFIG_PATH):/usr/src/mconf-aggr/config/config.json -ti mconf-aggr-webhook:$(TAG)

docker-run-zabbix:
	docker run --rm -v $(CONFIG_PATH):/usr/src/mconf-aggr/config/config.json -ti mconf-aggr-zabbix:$(TAG)

docker-build-dev:
	docker build -t mconf-aggr:dev .

docker-run-dev:
	docker run --rm -v $(AGGR_PATH):/usr/src/mconf-aggr/ -v $(CONFIG_PATH):/usr/src/mconf-aggr/config/config.json -ti mconf-aggr:dev

test:
	@python tests.py

dep:
	@pip install -r requirements.txt

html:
	@make -C docs/ html

lint:
	flake8 --exclude=.tox

.PHONY: clean
clean: clean-pyc clean-build

.PHONY:clean-pyc
clean-pyc:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	find . -name '*~' -exec rm --force  {} +

.PHONY: clean-build
clean-build:
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force --recursive *.egg-info
