#!/bin/bash

runpath="$(dirname $0)/../python/main.py -f"
fname="/tmp/$(date --iso-8601=seconds).txt"
candump -L can0 | tee $fname | python3 $runpath
