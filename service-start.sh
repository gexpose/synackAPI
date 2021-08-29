#!/bin/bash

set -m
echo "Starting services"
./start-polling.sh & 
sleep 60 # wait for above login process to complete


echo "Initiating mission bot"
./start-mission.sh 

fg %1