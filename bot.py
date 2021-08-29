#!/usr/bin/env python3
from synack import synack
import time
from slack import Slack

###### PLEASE READ THIS FIRST #####
## This is the URL you must read ##
## before using a bot. It gives  ##
## you the maximum API requests  ##
## allowed. If you exceed the 5- ##
## minute maximum, you are at    ##
## risk for being removed from   ##
## the platform in its entirety. ##
##                               ##
## IT IS ADVISED THAT YOU DO NOT ##
## POLL MORE THAN ONCE EVERY 10  ##
## SECONDS!!! PLEASE REVIEW THE  ##
## HELP CENTER ARTICLE!          ##
##                               ##

## https://support.synack.com/hc/en-us/articles/1500002201401-Mission-Automation-Throttling-MUST-READ ##

##                               ##
## YOU ALONE ARE RESPONSIBLE FOR ##
## MAKING SURE YOU DO NOT EXCEED ##
## THE MAXIMUM NUMBER OF ALLOWED ##
## API CALLS OVER THE SPECIFIED  ##
## PERIOD!                       ##
###################################

## This is a bare-bones mission ##
## bot. The sky is the limit on ##
## what options you want to add ##
## to it                        ##


## pollSleep will sleep for x  ##
## seconds after polling the   ##
## API for available missions  ##
pollSleep = 100

## claimSleep will sleep for y  ##
## seconds after attempting to  ##
## claim mission. This is used  ##
## to prevent hitting the max   ##
## API requests over any 5 min  ##
## period.                      ##
claimSleep = 100

s1 = synack()
s1.getSessionToken()

# register slack object to send mission details when claimed
slack = Slack()
print("Starting mission claim bot")
while True:
    time.sleep(pollSleep)
    missionJson = s1.pollMissions()
    if len(missionJson) == 0:
        continue
    missionList = s1.claimMission(missionJson)
    slack.send_alert_for_mission(missionList)
    time.sleep(claimSleep)
