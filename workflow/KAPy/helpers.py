import os
import glob
import sys
from collections.abc import Iterable
import yaml

def buildPath(cfg,thisDir, files=[]):
    '''
    Get full path
    
    Gets the full path of a directory key named in the configuration file
    '''
    #Build the path first
    if thisDir == "workDir":
        path=os.path.join(cfg['dirs']['workDir'])
    else:
        path=os.path.join(cfg['dirs']['workDir'],cfg['dirs'][thisDir])
    #Add file(s)
    if isinstance(files,str):
        rtn=os.path.join(path,files)
    elif isinstance(files,Iterable):
        if len(files)!=0:
            rtn=[os.path.join(path,f) for f in files]
        else:
            rtn=path
    else:
        sys.exit("Unsupported variable type supplied to KAPy.buildPath()")
    return(rtn)
        

def loadConfig(configfile='config.yaml',
               useDefaults=True,
               defaultFile='config/defaults.yaml'):
    '''
    Load config file
    
    Loads the KAPy config file specified in the yaml format. The use of system-wide defaults can
    be disabled with the 'useDefualts' switch - the path for the defaults is specified in 
    'defaultFile'
    '''
    #Load config file
    with open(configfile, 'r') as f:
    	cfg=yaml.safe_load(f)
    
    #If we are using defaults, load them as well and then merge the two dicts
    if useDefaults:
        #Load defaults
        with open(defaultFile, 'r') as f:
            dft=yaml.safe_load(f)
        #Previously we have done a partial update of the defaults, using a 
        #recursive function that digs down below the top level. This doesn't
        #work very well unfortunately, particularly when you want to exclude 
        #elements. Here we use a simple top-level replacement instead
        rtn=dft
        for key,values in cfg.items():
            rtn[key]=values
        return(rtn)
    else:
        return(cfg)

