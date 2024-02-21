import os
import glob
import sys
from collections.abc import Iterable

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
        rtn=[os.path.join(path,f) for f in files]
    else:
        sys.exit("Unsupported variable type supplied to KAPy.buildPath()")
    return(rtn)
        
