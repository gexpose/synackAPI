#!/usr/bin/env python3
## This is meant to be used from the docker image and it serves as a init process for the docker environment
## Config file is set statically to /root/.synack/synack.conf as per docker setup.
## If you want to use it as standalone you can remove the option and use this script to poll every 1 hour for new targets and auto register them.


###############################################
## THIS HAS NOTHING TO DO WITH `bot.py`!!!!! ##
###############################################

from synack import synack
import time

s1 = synack()
s1.configFile = "/root/.synack/synack.conf"
s1.connectToPlatform()
s1.getSessionToken()

# Let's go headless here
s1.headless = True
# Polling time set to 1 hour
pollSleep = 3600

while True:
    s1.getAllTargets()
    s1.registerAll()
    time.sleep(pollSleep)
