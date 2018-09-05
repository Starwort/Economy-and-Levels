#!/bin/bash
cp template.txt restart.txt
while [ -f restart.txt ]
do
    rm restart.txt
    git pull
    python3.6 main.py
done