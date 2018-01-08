#!/bin/bash

if [ ${AGGR_TYPE} = conf ]; \
  then \
    gunicorn main_event_listener:app
  else
    python main.py $@
	fi
##
