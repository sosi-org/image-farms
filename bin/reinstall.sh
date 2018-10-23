#!/usr/bin/env bash

source ifarms/bin/activate

pip install -r requirements.txt
cd tests
npm i
cd ..
