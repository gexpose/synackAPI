#!/usr/bin/env python3
import sys
from synack import synack
import time

s1 = synack()
s1.gecko = False
#s1.Proxy = True
s1.getSessionToken()
s1.getAllTargets()
args = len(sys.argv)
if args == 1:
    s1.connectToTarget("OPTIMUSDOWNLOAD")
elif args == 2:
    s1.connectToTarget(sys.argv[1])
else:
    print("Too many arguments")
