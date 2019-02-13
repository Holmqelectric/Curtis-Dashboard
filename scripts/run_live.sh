#!/bin/bash

fname="/tmp/$(date --iso-8601=seconds).txt"
candump -L can0 | tee $fname | python3 ../python/main.py
