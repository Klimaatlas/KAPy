#!/usr/bin/env python

#Setup KAPy directory structure

import KAPy
import os

#Load configuration 
config=KAPy.loadConfig()  

#Check that the working directory exists first
wkDir =config['dirs']['workDir']
if not os.path.exists(wkDir):
    print("Creating " + wkDir + "...")
    os.mkdir(wkDir)
else:
    print(wkDir + " already exists.")

#Setup sub directories directories
for d in config['dirs'].keys():
    thisDir=KAPy.buildPath(config,d)
    if not os.path.exists(thisDir):
        print("Creating " + thisDir + "...")
        os.mkdir(thisDir)
    else:
        print(thisDir + " already exists.")
            
