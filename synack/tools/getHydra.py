#!/usr/bin/env python3

from synack import synack
import os
import sys

def hydraOutput(codename):
    jsonResponse = s1.getHydra(codename)
    hydraOut = list()
    for i in range(len(jsonResponse)):
        keys = list(jsonResponse[i]['ports'].keys())
        for j in range(len(keys)):
            portKeys = list(jsonResponse[i]['ports'][keys[j]])
            for k in range(len(portKeys)):
                if len(jsonResponse[i]['ports'][keys[j]][portKeys[k]]) > 0:
                    hydraOut.append(jsonResponse[i]['ip']+":"+keys[j]+":"+portKeys[k])
    return hydraOut

s1 = synack()
s1.gecko = False
s1.getSessionToken()
s1.getAllTargets()
args = len(sys.argv)
if args == 2:
    codename = str(sys.argv[1].lower())
    output = hydraOutput(codename)
    with open("hydra.out", 'a') as out:
        out.write('\n'.join(output))
if args > 2:
    sys.exit()
if args == 1:
    codenames = s1.getCodenames("host")
    for codename in codenames:
        print(codename)
        targetPath = "./"+codename.upper()+"/"
        if os.path.isdir(targetPath) == False:
            os.mkdir(targetPath)
        output = hydraOutput(codename)
        with open(targetPath+"hydra.txt", 'a') as out:
            out.write('\n'.join(output))
