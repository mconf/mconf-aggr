#!/bin/bash

ACTION=DOCKER;

while getopts 'gdlh' c
do
  case $c in
    g) ./config/gen_file.sh/;;
    d) ACTION=DOCKER;;
    l) ACTION=LOCAL;;
    h) echo $(cat README.md); exit 0;;
    *) echo $(cat README.md); exit 1;;
  esac
done

case $ACTION in
    DOCKER) ./dev_docker.sh;;
    LOCAL)  ./dev_locally.sh;;
esac
