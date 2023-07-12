include .env

AGGR_PATH=$(shell pwd)
DOCKER_USERNAME?=mconf
REPOSITORY?=mconf-aggr
FULL_VERSION?=$(shell cat .version)
REVISION?=$(shell git rev-parse --short HEAD)
IMAGE_NAME=$(DOCKER_USERNAME)/$(REPOSITORY)
IMAGE_VERSION=$(FULL_VERSION)-$(REVISION)

run:
	gunicorn main:app --bind=0.0.0.0:8000 --worker-class gevent

up:
	docker-compose up -d prod

up-dev:
	docker-compose up -d dev

up-debug:
	docker-compose up -d debug

docker-build:
	docker-compose build prod

docker-build-dev:
	docker-compose build dev

docker-build-debug:
	docker-compose build debug

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

test:
	pdm run python tests.py ${ARGS}

html:
	@make -C docs/ html

lint:
	pdm run isort . --check-only
	pdm run flake8

format:
	pdm run black .
	pdm run isort .

clean:
	@find . -type d -name __pycache__ -exec rm -rf {} +
	@find . -type d -name .pytest_cache -exec rm -rf {} +
	@find . -type f -name '*.py[co]' -delete