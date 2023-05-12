""" Configuration management """

import configparser
import os,glob,sys

def loadConfig(path,type):
    """
    Load a configuration file from the default location
    
    Returns a configparser representation of the configuration file
    """    
    match type:
        case 'config':
            iniFile = os.path.join(path,'config.ini')
        case 'ESGF':
            iniFile = os.path.join(path,'ESGF.ini')
            
    if(not(os.path.exists(iniFile))):
        sys.exit('Cannot file configuration file: ' + iniFile)
        

    #Load the file
    thisCfg=configparser.ConfigParser()
    thisCfg.read(iniFile)
    
    #Finished
    return thisCfg

        