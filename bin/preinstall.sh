#!/usr/bin/env bash
set -e
# ########################################################
# Run this after the first clone.
# ########################################################


bash ./bin/util/assert-right-path
bash ./bin/util/assert-infrastructure
bash ./bin/util/cleanup-fresh
pwd


#installs python
virtualenv -p /usr/bin/python3.5  ifarms
./bin/reinstall.sh
