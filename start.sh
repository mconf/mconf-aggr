#!/bin/sh

if [ -z ${AGGR_APP} ]; then
    exit 1
fi

case "${AGGR_APP}" in
    webhook)
        gunicorn main:app --bind=0.0.0.0:8000 --worker-class gevent;;
    *)
        exit 1;;
esac
