#!/usr/bin/env bash

# ########################################################
# Tests the microserviec.
#      (Run only after ./bin/start_serive.sh )
# ########################################################

bash ./bin/util/assert-right-path

cd tests
# IMAGESTORE ENV variable used by client to check if the files are created/deleted. (By physically checking the file system)
export IMAGESTORE="../imagestore"
node ./api-test.js
cd ..
