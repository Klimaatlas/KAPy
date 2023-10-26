import os
import KAPy

def buildPath(cfg,thisDir, *p):
    '''
    Get full path
    
    Gets the full path of a directory key named in the configuration file
    '''
    if thisDir == "outputDir":
        return(os.path.join(cfg['dirs']['outputDir'],*p))
    else:
        return(os.path.join(cfg['dirs']['outputDir'],cfg['dirs'][thisDir],*p))
   