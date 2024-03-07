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
        

def loadConfig(configfile='config.yaml'):
    '''
    Load config file
    
    Loads the KAPy config file specified in the yaml format.
    '''
    
    #Load config file
    with open(configfile, 'r') as f:
    	cfg=yaml.safe_load(f)
    
    return(cfg)

