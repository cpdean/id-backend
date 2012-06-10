#!/bin/bash

#naive dependency check
if [ ! -d "v" ]; then
    virtualenv v
    pip install -r requirements.txt -E v
fi
source v/Scripts/activate
