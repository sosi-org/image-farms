#!/usr/bin/env bash
# ! / usr/bin/bash

# ########################################################
# Starts the microservice.
#      (After this, you can run  ./bin/test_api.sh)
# ########################################################


bash ./bin/util/assert-right-path

source ifarms/bin/activate
cd service
python3 api.py
cd ..
