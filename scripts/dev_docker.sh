#!/bin/bash
set -e

pushd $MC_AGGR
make docker-run-dev IMAGE_VERSION=dev-latest
popd
