import os

def getFullPath(cfg,thisDir):
    '''
    Get full path
    
    Gets the full path of a directory key named in the configuration file
    '''
    if thisDir == "outputDir":
        return(cfg['dirs']['outputDir'])
    else:
        return(os.path.join(cfg['dirs']['outputDir'],cfg['dirs'][thisDir]))
