AGGR_PATH=$(shell pwd)
IMAGE_WORKDIR=/usr/src/mconf-aggr
LOGGING_PATH?=mconf_aggr/logging.json
DOCKER_USERNAME?=mconf
REPOSITORY?=mconf-aggr
FULL_VERSION?=$(shell cat .version)
NUMBER_VERSION?=$(shell cat .version | cut -d '-' -f 1)
MAJOR_VERSION?=$(shell cat .version | cut -d '.' -f 1)
STAGE_VERSION?=$(shell cat .version | sed -n -r "s/[^-]*-(.+)$$/\1/p")
REVISION?=$(shell git rev-parse --short HEAD)
IMAGE_NAME?=$(DOCKER_USERNAME)/$(REPOSITORY)
IMAGE_VERSION?=$(FULL_VERSION)-$(REVISION)

run:
	gunicorn main:app --bind=0.0.0.0:8000 --worker-class gevent

up:
	IMAGE_NAME=$(IMAGE_NAME) \
	MCONF_AGGR_WEBHOOK_IMAGE_VERSION=webhook-$(IMAGE_VERSION) \
	docker-compose -f production.yml up

start:
	docker-compose -f production.yml start ${SERVICE}

restart:
	docker-compose -f production.yml restart ${SERVICE}

stop:
	docker-compose -f production.yml stop ${SERVICE}

docker-build:
	docker build -f Dockerfile -t $(IMAGE_NAME):webhook-$(IMAGE_VERSION) .
	docker tag $(IMAGE_NAME):webhook-$(IMAGE_VERSION) $(IMAGE_NAME):webhook-latest

docker-build-dev:
	docker build -f Dockerfile.dev -t $(IMAGE_NAME):dev .
	docker tag $(IMAGE_NAME):dev $(IMAGE_NAME):dev-latest
	docker image rm `docker images -f dangling=true -a -q`

docker-run:
	docker run --rm \
	-v $(AGGR_PATH)/$(LOGGING_PATH):$(IMAGE_WORKDIR)/$(LOGGING_PATH) \
	-p 8000:8000 \
	--env-file=envs/webhook-env-file.env \
	-ti $(IMAGE_NAME):webhook-$(IMAGE_VERSION)

docker-run-dev:
	AGGR_PATH=$(AGGR_PATH) \
	IMAGE_NAME=$(IMAGE_NAME):dev \
	MCONF_AGGR_WEBHOOK_IMAGE_VERSION=dev \
	docker-compose -f development.yml up

docker-tag:
	docker tag $(IMAGE_NAME):webhook-$(IMAGE_VERSION) $(IMAGE_NAME):webhook-$(NUMBER_VERSION)
	docker tag $(IMAGE_NAME):webhook-$(IMAGE_VERSION) $(IMAGE_NAME):webhook-$(MAJOR_VERSION)
	docker tag $(IMAGE_NAME):webhook-$(IMAGE_VERSION) $(IMAGE_NAME):webhook-$(REVISION)
	docker tag $(IMAGE_NAME):webhook-$(IMAGE_VERSION) $(IMAGE_NAME):webhook-latest

docker-push: docker-tag
	docker push $(IMAGE_NAME):webhook-$(NUMBER_VERSION)
	docker push $(IMAGE_NAME):webhook-$(MAJOR_VERSION)
	docker push $(IMAGE_NAME):webhook-$(REVISION)
	docker push $(IMAGE_NAME):webhook-latest

docker-tag-unstable:
	docker tag $(IMAGE_NAME):webhook-$(IMAGE_VERSION) $(IMAGE_NAME):webhook-$(FULL_VERSION)

docker-push-unstable: docker-tag-unstable
	docker push $(IMAGE_NAME):webhook-$(FULL_VERSION)
	docker push $(IMAGE_NAME):webhook-$(REVISION)

docker-tag-latest:
	docker tag $(IMAGE_NAME):webhook-$(IMAGE_VERSION) $(IMAGE_NAME):webhook-latest

docker-push-latest: docker-tag-latest
	docker push $(IMAGE_NAME):webhook-latest

docker-tag-staging:
	docker tag $(IMAGE_NAME):webhook-$(IMAGE_VERSION) $(IMAGE_NAME):webhook-staging

docker-push-staging: docker-tag-staging
	docker push $(IMAGE_NAME):webhook-staging

.PHONY:docker-image
docker-image:
	@docker image ls $(IMAGE_NAME)*

.PHONY:docker-container-rm
docker-container-rm:
	@docker container stop `docker container ls -a -q`
	@docker container rm `docker container ls -a -q`

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
