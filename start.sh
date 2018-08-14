#!/bin/bash

if [ -z ${AGGR_APP} ]; then
    exit 1
fi

echo "ok"

case "${AGGR_APP}" in
    webhook)
        gunicorn main_webhook:app --bind=0.0.0.0:8000;;
    zabbix)
        python main_zabbix.py $@;;
    *)
        exit 1;;
esac
