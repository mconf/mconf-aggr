AGGR_PATH=$(shell pwd)
CONFIG_PATH=$(AGGR_PATH)/config/config.json
IMAGE_WORKDIR=/usr/src/mconf-aggr
DOCKER_USERNAME?=mconf
REPOSITORY?=mconf-aggr
FULL_VERSION?=$(shell cat .version)
NUMBER_VERSION?=$(shell cat .version | cut -d '-' -f 1)
MAJOR_VERSION?=$(shell cat .version | cut -d '.' -f 1)
STAGE_VERSION?=$(shell cat .version | sed -n -r "s/[^-]*-(.+)$$/\1/p")
REVISION?=$(shell git rev-parse --short HEAD)
IMAGE_NAME?=$(DOCKER_USERNAME)/$(REPOSITORY)
IMAGE_VERSION?=$(FULL_VERSION)-$(REVISION)
LOCAL_TAG?=$(APP)-$(IMAGE_VERSION)

ifndef APP
$(error APP variable is not set)
endif

run:
	python main_$(APP).py -c $(CONFIG_PATH)

up:
	IMAGE_NAME=$(IMAGE_NAME) \
	MCONF_AGGR_WEBHOOK_IMAGE_VERSION=webhook-$(IMAGE_VERSION) \
	MCONF_AGGR_ZABBIX_IMAGE_VERSION=zabbix-$(IMAGE_VERSION) \
	docker-compose -f production.yml up

start:
	docker-compose -f production.yml start ${SERVICE}

restart:
	docker-compose -f production.yml restart ${SERVICE}

stop:
	docker-compose -f production.yml stop ${SERVICE}

docker-build:
	docker build -f Dockerfile.dockerize.$(APP) -t $(IMAGE_NAME):$(LOCAL_TAG) .
	docker image rm `docker images -f dangling=true -a -q`
	docker tag $(IMAGE_NAME):$(LOCAL_TAG) $(IMAGE_NAME):$(APP)-latest

docker-run:
	docker run --rm -v $(CONFIG_PATH):$(IMAGE_WORKDIR)/config/config.json -ti $(IMAGE_NAME):$(LOCAL_TAG)

docker-run-dev:
	docker run --rm -v $(CONFIG_PATH):$(IMAGE_WORKDIR)/config/config.json -v $(AGGR_PATH):$(IMAGE_WORKDIR)/ --env AGGR_APP=$(AGGR_APP) $(EXTRA_OPTS) -ti $(IMAGE_NAME):$(LOCAL_TAG)

docker-tag:
	docker tag $(IMAGE_NAME):$(LOCAL_TAG) $(IMAGE_NAME):$(APP)-$(NUMBER_VERSION)
	docker tag $(IMAGE_NAME):$(LOCAL_TAG) $(IMAGE_NAME):$(APP)-$(MAJOR_VERSION)
	docker tag $(IMAGE_NAME):$(LOCAL_TAG) $(IMAGE_NAME):$(APP)-$(REVISION)
	docker tag $(IMAGE_NAME):$(LOCAL_TAG) $(IMAGE_NAME):$(APP)-latest

docker-push: docker-tag
	docker push $(IMAGE_NAME):$(APP)-$(NUMBER_VERSION)
	docker push $(IMAGE_NAME):$(APP)-$(MAJOR_VERSION)
	docker push $(IMAGE_NAME):$(APP)-$(REVISION)
	docker push $(IMAGE_NAME):$(APP)-latest

docker-tag-unstable:
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

.PHONY:docker-image
docker-image:
	@docker image ls $(IMAGE_NAME)*

.PHONY:docker-rm
docker-rm:
	@docker image rm -f `docker image ls mconf/mconf-aggr* -q`

.PHONY: docker-rm-dangling
docker-rm-dangling:
	@docker image rm `docker images -f dangling=true -a -q`

.PHONY:docker-prune
docker-prune:
	@docker system prune -f

.PHONY:docker-clean
docker-clean: docker-rm-dangling docker-rm docker-prune

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
