#!/bin/bash
pushd $MC_AGGR/scripts
ACTION=DOCKER;
SHOULD_REGISTER=false
GENERATE=false
NGROK=false

while getopts 'gdlrnh' c
do
  case $c in
    g) 	GENERATE=true;;
    d)  ACTION=DOCKER;;
    l)  ACTION=LOCAL;;
    r)  SHOULD_REGISTER=true;;
    n)  NGROK=true;;
    h)  echo $(cat README.md); exit 0;;
    *)  echo $(cat README.md); exit 1;;
  esac
done

if [[ $NGROK == "true" ]]; then
  ./utils/ngrok http 8000 > /dev/null &
  sleep 2
fi

if [[ $GENERATE == "true" ]]; then
  ./config/gen_file.sh -r $SHOULD_REGISTER
fi

case $ACTION in
    DOCKER) ./dev_docker.sh;;
    LOCAL)  ./dev_locally.sh;;
esac

popd
