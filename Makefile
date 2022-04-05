include .env

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
IMAGE_NAME=$(DOCKER_USERNAME)/$(REPOSITORY)
IMAGE_VERSION=$(FULL_VERSION)-$(REVISION)

run:
	gunicorn main:app --bind=0.0.0.0:8000 --worker-class gevent

up:
	IMAGE_NAME=$(IMAGE_NAME) \
	MCONF_AGGR_WEBHOOK_IMAGE_VERSION=webhook-$(IMAGE_VERSION) \
	docker-compose -f production.yml up

up-dev:
	docker-compose -f development.yml up

up-debug:
	docker-compose -f debugging.yml up

start:
	docker-compose -f production.yml start ${SERVICE}

restart:
	docker-compose -f production.yml restart ${SERVICE}

stop:
	docker-compose -f production.yml stop ${SERVICE}

docker-build-dev:
	$(MAKE) .docker-build PROJECT_ENV=development TAG_NAME=dev IMAGE_VERSION=""

docker-build-debug:
	$(MAKE) .docker-build PROJECT_ENV=debug TAG_NAME=debug IMAGE_VERSION=""

docker-build-prod:
	$(MAKE) .docker-build PROJECT_ENV=production TAG_NAME=webhook \
		IMAGE_VERSION="-$(IMAGE_VERSION)"

.docker-build-base:
	docker build -f Dockerfile.base \
		--build-arg PYTHON_VERSION=$(PYTHON_VERSION) \
		--build-arg POETRY_VERSION=$(POETRY_VERSION) \
		--build-arg POETRY_HOME=${POETRY_HOME} \
		--build-arg BASE_PATH=${BASE_PATH} \
		--build-arg APP_NAME=${APP_NAME} \
		-t mconf-aggr-base .

.docker-build: .docker-build-base
	docker build -f Dockerfile.${PROJECT_ENV} \
		--build-arg PYTHON_VERSION=$(PYTHON_VERSION) \
		--build-arg BASE_PATH=${BASE_PATH} \
		--build-arg APP_NAME=${APP_NAME} \
		-t $(IMAGE_NAME):$(TAG_NAME)$(IMAGE_VERSION) .
	docker tag $(IMAGE_NAME):$(TAG_NAME)$(IMAGE_VERSION) \
		$(IMAGE_NAME):$(TAG_NAME)-latest

docker-run-dev:
	$(MAKE) .docker-run PROJECT_ENV=development TAG_NAME=dev

docker-run-debug:
	$(MAKE) .docker-run PROJECT_ENV=debug TAG_NAME=debug

docker-run-prod:
	docker run --rm \
	-v $(AGGR_PATH)/$(LOGGING_PATH):$(IMAGE_WORKDIR)/$(LOGGING_PATH) \
	-p 8000:8000 \
	--env-file=envs/webhook-env-file.env \
	-ti $(IMAGE_NAME):webhook-$(IMAGE_VERSION)

.docker-run:
	AGGR_PATH=$(AGGR_PATH) \
	IMAGE_NAME=$(IMAGE_NAME):$(TAG_NAME) \
	MCONF_AGGR_WEBHOOK_IMAGE_VERSION=$(TAG_NAME) \
	docker-compose -f $(PROJECT_ENV).yml up

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
	poetry run python tests.py

install_requisites_locally:
	curl -sSL https://install.python-poetry.org | POETRY_HOME="" POETRY_VIRTUALENVS_CREATE=true python3 -

install_requisites:
	curl -sSL https://install.python-poetry.org | python3 -
	export PATH="${POETRY_HOME}/bin:${PATH}"

install_deps_locally:
	POETRY_VIRTUALENVS_CREATE=true \
	poetry install --no-root ${INSTALL_DEPS_ARGS}

install_deps:
	poetry install --no-root ${INSTALL_DEPS_ARGS}

html:
	@make -C docs/ html

lint:
	poetry run isort . --check-only
	poetry run flake8

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
