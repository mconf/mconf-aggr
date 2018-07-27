#!/bin/bash

if [ -z ${AGGR_TYPE} ]; then
    exit 1
fi

if [ ${AGGR_TYPE} = conf ]; then
    gunicorn main_event_listener:app
else
    python main.py $@
fi
