#!/usr/bin/env bash
set -e
# ########################################################
# Run this if you pulled/updated the pakage info files.
#     (Creates the virtualenv environment)
# ########################################################


#assert npm installed
npm help >/dev/null

bash ./bin/util/assert-right-path

source ifarms/bin/activate

pip install -r requirements.txt
cd tests
npm i
cd ..
