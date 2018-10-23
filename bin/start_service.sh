#!/usr/bin/env bash
# ! / usr/bin/bash

source ifarms/bin/activate
cd service
python3 api.py &
cd ..
