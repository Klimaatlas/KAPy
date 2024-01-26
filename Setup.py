#Setup KAPy directory structure

import KAPy
import os

#Configuratioon -----------------------
#Load configuration 
config=KAPy.loadConfig()  

#Setup directories
for d in config['dirs'].keys():
    thisDir=KAPy.buildPath(config,d)
    if not os.path.exists(thisDir):
        os.mkdir(thisDir)
