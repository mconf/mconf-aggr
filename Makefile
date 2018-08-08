CONFIG_PATH=~/config.json
AGGR_PATH=$(shell pwd)
DOCKER_USERNAME?=mconftec
REPOSITORY?=mconf-aggr
FULL_VERSION?=$(shell cat version)
MAJOR_VERSION?=$(shell cat version | cut -d '.' -f 1)
REVISION?=$(shell git rev-parse --short HEAD)

ifndef APP
$(error APP variable is not set)
endif

run:
	python main_$(APP).py -c $(CONFIG_PATH)

docker-build:
	docker build -f Dockerfile.$(APP) -t $(DOCKER_USERNAME)/$(REPOSITORY):$(APP)-latest .

docker-run:
	docker run --rm -v $(CONFIG_PATH):/usr/src/mconf-aggr/config/config.json -ti $(DOCKER_USERNAME)/$(REPOSITORY):$(APP)-latest

docker-tag:
	docker tag $(DOCKER_USERNAME)/$(REPOSITORY):$(APP)-latest $(DOCKER_USERNAME)/$(REPOSITORY):$(APP)-$(FULL_VERSION)
	docker tag $(DOCKER_USERNAME)/$(REPOSITORY):$(APP)-latest $(DOCKER_USERNAME)/$(REPOSITORY):$(APP)-$(MAJOR_VERSION)
	docker tag $(DOCKER_USERNAME)/$(REPOSITORY):$(APP)-latest $(DOCKER_USERNAME)/$(REPOSITORY):$(APP)-$(REVISION)

docker-push: docker-tag
	docker push $(DOCKER_USERNAME)/$(REPOSITORY):$(APP)-latest
	docker push $(DOCKER_USERNAME)/$(REPOSITORY):$(APP)-$(FULL_VERSION)
	docker push $(DOCKER_USERNAME)/$(REPOSITORY):$(APP)-$(MAJOR_VERSION)
	docker push $(DOCKER_USERNAME)/$(REPOSITORY):$(APP)-$(REVISION)

.PHONY:tags
tags:
	@echo "$(DOCKER_USERNAME)/$(REPOSITORY):$(APP)-latest"
	@echo "$(DOCKER_USERNAME)/$(REPOSITORY):$(APP)-$(FULL_VERSION)"
	@echo "$(DOCKER_USERNAME)/$(REPOSITORY):$(APP)-$(MAJOR_VERSION)"
	@echo "$(DOCKER_USERNAME)/$(REPOSITORY):$(APP)-$(REVISION)"

test:
	@python tests.py

dep:
	@pip install -r requirements_webhook.txt
	@pip install -r requirements_zabbix.txt

html:
	@make -C docs/ html

lint:
	@flake8 --exclude=.tox

.PHONY: clean
clean: clean-pyc clean-build

.PHONY:clean-pyc
clean-pyc:
	@find . -name '*.pyc' -exec rm --force {} +
	@find . -name '*.pyo' -exec rm --force {} +
	@find . -name '*~' -exec rm --force  {} +

.PHONY: clean-build
clean-build:
	@rm --force --recursive build/
	@rm --force --recursive dist/
	@rm --force --recursive *.egg-info
