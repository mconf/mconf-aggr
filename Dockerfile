ARG DISABLE_DEV
ARG PYTHON_IMAGE_TAG=3.10
ARG PDM_VERSION=2.6.1
ARG PDM_HOME=/opt/pdm
ARG BASE_PATH=/usr/src
ARG APP_NAME=mconf-aggr

#
# Stage: base
#
FROM python:${PYTHON_IMAGE_TAG} as base
ARG PYTHON_IMAGE_TAG
ARG PDM_VERSION
ARG PDM_HOME
ARG DISABLE_DEV

ENV PDM_VERSION=$PDM_VERSION \
    PDM_HOME=$PDM_HOME

# Install PDM using PDM_VERSION and PDM_HOME
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir pdm==${PDM_VERSION} \
    && pdm config python.use_venv false

WORKDIR /opt/python
COPY pdm.lock pyproject.toml ./

RUN pdm config python.use_venv false
RUN pdm install --no-editable $([ ${DISABLE_DEV:-0} = 1 ] && echo "--prod" )
COPY ./mconf_aggr ./mconf_aggr

ENV PYTHONPATH=/opt/python/__pypackages__/${PYTHON_IMAGE_TAG}/lib
ENV PATH=/opt/python/__pypackages__/${PYTHON_IMAGE_TAG}/bin:$PATH

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

#
# Stage: build
#
FROM base as build

WORKDIR /opt/python
RUN pdm build --no-sdist
RUN pdm export -o constraints.txt --without-hashes

EXPOSE 8000

#
# Stage: production
#
FROM python:${PYTHON_IMAGE_TAG}-slim-bullseye as production
ARG BASE_PATH
ARG APP_NAME

ENV LOGURU_LOG_LEVEL=INFO
ENV LOGURU_LOG_SINK=sink_serializer

WORKDIR $BASE_PATH/$APP_NAME

COPY --from=build /opt/python/dist/*.whl ./
COPY --from=build /opt/python/constraints.txt ./

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN pip install ./mconf_aggr*.whl --constraint constraints.txt \
    && rm $(ls | grep -i '.whl$') constraints.txt

ENTRYPOINT ["gunicorn", "mconf_aggr.main:app", "--bind=0.0.0.0:8000", "--worker-class", "gevent"]

#
# Stage: development
#
FROM base as development
ARG BASE_PATH
ARG APP_NAME

ENV LOGURU_LOG_LEVEL=DEBUG
ENV LOGURU_LOG_SINK=sys.stderr

WORKDIR $BASE_PATH/$APP_NAME
COPY mconf_aggr/ ./mconf_aggr

ENTRYPOINT ["gunicorn", "mconf_aggr.main:app", "--bind=0.0.0.0:8000", "--worker-class", "gevent"]

#
# Stage: debug
#
FROM base as debug
ARG BASE_PATH
ARG APP_NAME

ENV LOGURU_LOG_LEVEL=DEBUG
ENV LOGURU_LOG_SINK=sys.stderr

WORKDIR $BASE_PATH/$APP_NAME
COPY mconf_aggr/ ./mconf_aggr

EXPOSE 5678

ENV GEVENT_SUPPORT=True

ENTRYPOINT ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", \
            "--wait-for-client", "-m"]
CMD ["gunicorn", "mconf_aggr.main:app", "--bind=0.0.0.0:8000", \
     "--worker-class", "gevent"]
