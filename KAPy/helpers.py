import os
import KAPy
import glob

def buildPath(cfg,thisDir, *p):
    '''
    Get full path
    
    Gets the full path of a directory key named in the configuration file
    '''
    if thisDir == "outputDir":
        return(os.path.join(cfg['dirs']['outputDir'],*p))
    else:
        return(os.path.join(cfg['dirs']['outputDir'],cfg['dirs'][thisDir],*p))

def listFiles(cfg,thisDir,pattern='*'):
    '''
    Get files by path
    
    Lists the files present in a folder, where the folder is identified
    by the directory key named in the configuration file
    '''
    return glob.glob(KAPy.buildPath(cfg,thisDir,pattern))