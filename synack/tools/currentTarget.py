#!/usr/bin/env python3
from synack import synack

s1 = synack()
s1.gecko = False
s1.getSessionToken()
s1.getAllTargets()
response = s1.try_requests("GET", "https://platform.synack.com/api/launchpoint", 10)
jsonResponse=response.json()
status = jsonResponse['status']
if 'slug' in jsonResponse:
    currentTarget = s1.getCodenameFromSlug(jsonResponse['slug'])
    futureTarget = s1.getCodenameFromSlug(jsonResponse['pending_slug'])
else:
    print("Not connected")
if currentTarget == None:
    print("Not connected")
if(status != "connected"):
    print("Not connected to target.")
else:
    if(futureTarget != None):
        print("Disconnecteding from "+currentTarget+" and connecting to "+futureTarget+".")
    else:
        print("Connected to "+currentTarget+".")
