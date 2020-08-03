#!/bin/bash

pushd $MC_AGGR/scripts
ngrok=$(./utils/ngrok_url.sh)
ip=$(./utils/myip.sh)

while getopts 'r:' c
do
  case $c in
    r)	if [[ $OPTARG == "false" || $OPTARG == "true" ]]; then
			SHOULD_REGISTER=$OPTARG
		else
			echo "-r parameter accepts only 'false' or 'true'."
			exit 1
		fi;;
	*)	echo "gen_file.sh -r [true|false]"
		exit 1;
  esac
done

if [[ -z "$ngrok" || $ngrok == "null" ]]; then
	echo "ngrok is not running"
fi

echo "IP: $ip"
echo "ngrok: $ngrok"

cd $MC_AGGR/envs
echo "MCONF_WEBHOOK_CALLBACK_URL=$ngrok" > webhook-env-file.env 
echo "MCONF_WEBHOOK_SHOULD_REGISTER=$SHOULD_REGISTER" >> webhook-env-file.env
echo "MCONF_WEBHOOK_DATABASE_HOST=$ip" >> webhook-env-file.env
echo "MCONF_WEBHOOK_DATABASE_USER=mconf" >> webhook-env-file.env
echo "MCONF_WEBHOOK_DATABASE_PASSWORD=postgres" >> webhook-env-file.env
echo "MCONF_WEBHOOK_DATABASE_DATABASE=mconf" >> webhook-env-file.env
echo "MCONF_WEBHOOK_DATABASE_PORT=5432" >> webhook-env-file.env
echo "MCONF_WEBHOOK_ROUTE=/" >> webhook-env-file.env
echo "MCONF_WEBHOOK_AUTH_REQUIRED=true" >> webhook-env-file.env
echo "MCONF_WEBHOOK_LOG_LEVEL=DEBUG" >> webhook-env-file.env
popd
