#!/usr/bin/env python3

## This pulls down Hydra information on targets,
## taking 0 or 1 arguments. The one argument is
## a single codename. If a codename isn't given,
## this will return the Hydra information for all
## host assessment targets.

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

# The following are required
s1 = synack()
s1.gecko = False
s1.getSessionToken()
s1.getAllTargets()
args = len(sys.argv)

## One command line argument is given. This needs to be the
## codename of a target. This will save a file `hydra.out`
## to the working directory. If Hydra identified any open
## ports, the file will contain the IP:PORT:[TCP/UDP] for
## each record; one per line.

if args == 2:
    codename = str(sys.argv[1].lower())
    output = hydraOutput(codename)
    with open("hydra.out", 'a') as out:
        out.write('\n'.join(output))

## More than one command line argument will cause this script
## to end

if args > 2:
    sys.exit()

## With no command line arguments given this script will
## create a directory for each host-assessment as ./CODENAME/.
## The same hydra.out file will be created for each target
## in their respective CODENAME directories.
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
