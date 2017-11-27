AGGR_PATH=~/mconf-aggr
CONFIG_PATH=~/config.json
AGGR_PATH=$(shell realpath .)

run:
	@python main.py -c $(CONFIG_PATH)

test:
	@python tests.py

dep:
	@pip install -r requirements.txt

html:
	@make -C docs/ html

docker-build:
	docker build -t mconf-aggr:$(TAG) .

docker-build-dev:
	docker build -t mconf-aggr:dev .

docker-run:
	docker run --rm -v $(CONFIG_PATH):/usr/src/mconf-aggr/config/config.json -ti mconf-aggr:$(TAG)

docker-run-dev:
	docker run --rm -v $(AGGR_PATH):/usr/src/mconf-aggr/ -v $(CONFIG_PATH):/usr/src/mconf-aggr/config/config.json -ti mconf-aggr:dev

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
