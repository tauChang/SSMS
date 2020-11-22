#!/usr/bin/env bash

export PYTHONPATH=$(pwd)/../../src/:$(pwd)
echo $PYTHONPATH
python2.7 main.py
