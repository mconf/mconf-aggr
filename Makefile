CONFIG_PATH=~/config.json
AGGR_PATH=$(shell pwd)
DOCKER_USERNAME?=mconftec
REPOSITORY?=mconf-aggr
FULL_VERSION?=$(shell cat .version)
NUMBER_VERSION?=$(shell cat .version | cut -d '-' -f 1)
MAJOR_VERSION?=$(shell cat .version | cut -d '.' -f 1)
STAGE_VERSION?=$(shell cat .version | sed -n -r "s/[^-]*-(.+)$$/\1/p")
REVISION?=$(shell git rev-parse --short HEAD)
IMAGE_NAME=$(DOCKER_USERNAME)/$(REPOSITORY)
LOCAL_TAG=$(APP)-$(FULL_VERSION)-$(REVISION)

ifndef APP
$(error APP variable is not set)
endif

run:
	python main_$(APP).py -c $(CONFIG_PATH)

docker-build:
	docker build -f Dockerfile.$(APP) -t $(IMAGE_NAME):$(LOCAL_TAG) .

docker-run:
	docker run --rm -v $(CONFIG_PATH):/usr/src/mconf-aggr/config/config.json -ti $(IMAGE_NAME):$(LOCAL_TAG)

docker-tag: docker-build
	docker tag $(IMAGE_NAME):$(LOCAL_TAG) $(IMAGE_NAME):$(APP)-$(NUMBER_VERSION)
	docker tag $(IMAGE_NAME):$(LOCAL_TAG) $(IMAGE_NAME):$(APP)-$(MAJOR_VERSION)
	docker tag $(IMAGE_NAME):$(LOCAL_TAG) $(IMAGE_NAME):$(APP)-$(REVISION)
	docker tag $(IMAGE_NAME):$(LOCAL_TAG) $(IMAGE_NAME):$(APP)-latest

docker-push: docker-tag
	docker push $(IMAGE_NAME):$(APP)-$(NUMBER_VERSION)
	docker push $(IMAGE_NAME):$(APP)-$(MAJOR_VERSION)
	docker push $(IMAGE_NAME):$(APP)-$(REVISION)
	docker push $(IMAGE_NAME):$(APP)-latest

docker-tag-unstable: docker-build
	docker tag $(IMAGE_NAME):$(LOCAL_TAG) $(IMAGE_NAME):$(APP)-$(FULL_VERSION)
	docker tag $(IMAGE_NAME):$(LOCAL_TAG) $(IMAGE_NAME):$(APP)-$(REVISION)

docker-push-unstable: docker-tag-unstable
	docker push $(IMAGE_NAME):$(APP)-$(FULL_VERSION)
	docker push $(IMAGE_NAME):$(APP)-$(REVISION)

.PHONY:tags
tags:
	@echo "$(IMAGE_NAME):$(APP)-$(NUMBER_VERSION)"
	@echo "$(IMAGE_NAME):$(APP)-$(MAJOR_VERSION)"
	@echo "$(IMAGE_NAME):$(APP)-$(REVISION)"
	@echo "$(IMAGE_NAME):$(APP)-latest"

.PHONY:tags-unstable
tags-unstable:
	@echo "$(IMAGE_NAME):$(APP)-$(FULL_VERSION)"
	@echo "$(IMAGE_NAME):$(APP)-$(REVISION)"

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
