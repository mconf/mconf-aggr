#!/bin/bash
pushd $MC_AGGR/scripts
ACTION=DOCKER;
SHOULD_REGISTER=false
GENERATE=false
NGROK=false

while getopts 'gdlr:n:h' c
do
  case $c in
    g) 	GENERATE=true;;
    d)  ACTION=DOCKER;;
    l)  ACTION=LOCAL;;
    r)  if [[ $OPTARG == "false" || $OPTARG == "true" ]]; then
          SHOULD_REGISTER=$OPTARG
        else
          echo "-r parameter accepts only 'false' or 'true'."
          exit 1
        fi;;
    n)  if [[ $OPTARG == "false" || $OPTARG == "true" ]]; then
          NGROK=$OPTARG
        else
          echo "-n parameter accepts only 'false' or 'true'."
          exit 1
        fi;;
    h)  echo $(cat README.md); exit 0;;
    *)  echo $(cat README.md); exit 1;;
  esac
done

if [[ $NGROK == "true" ]]; then
  ./utils/ngrok http 8080 > /dev/null &
fi

if [[ $GENERATE == "true" ]]; then
  ./config/gen_file.sh -r $SHOULD_REGISTER
fi

case $ACTION in
    DOCKER) ./dev_docker.sh;;
    LOCAL)  ./dev_locally.sh;;
esac

popd
