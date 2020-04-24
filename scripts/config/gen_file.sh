#!/bin/bash

ngrok=$(../utils/ngrok_url.sh)
ip=$(../utils/myip.sh)

if [ -z "$ngrok" ]; then
	echo "ngrok is not running"
fi

pushd $MC_AGGR/envs
echo "MCONF_WEBHOOK_CALLBACK_URL=$ngrok" > webhook-env-file.env 
echo "MCONF_WEBHOOK_SHOULD_REGISTER=false" >> webhook-env-file.env
echo "MCONF_WEBHOOK_DATABASE_HOST=$ip" >> webhook-env-file.env
echo "MCONF_WEBHOOK_DATABASE_USER=mconf" >> webhook-env-file.env
echo "MCONF_WEBHOOK_DATABASE_PASSWORD=postgres" >> webhook-env-file.env
echo "MCONF_WEBHOOK_DATABASE_DATABASE=mconf" >> webhook-env-file.env
echo "MCONF_WEBHOOK_DATABASE_PORT=5432" >> webhook-env-file.env
echo "MCONF_WEBHOOK_ROUTE=/" >> webhook-env-file.env
echo "MCONF_WEBHOOK_AUTH_REQUIRED=true" >> webhook-env-file.env
echo "MCONF_WEBHOOK_LOG_LEVEL=DEBUG" >> webhook-env-file.env
popd
