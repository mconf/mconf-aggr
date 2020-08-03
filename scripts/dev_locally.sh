#!/bin/bash
set -e

pushd $MC_AGGR
source ./venv/bin/activate
make run
popd