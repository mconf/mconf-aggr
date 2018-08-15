#!/bin/bash

if [ -z ${AGGR_APP} ]; then
    exit 1
fi

case "${AGGR_APP}" in
    webhook)
        PYTHONPATH=. gunicorn main_webhook:app --bind=0.0.0.0:8000 --config=gunicorn_config.py;;
    zabbix)
        python main_zabbix.py $@;;
    *)
        exit 1;;
esac
