""" Configuration management """

import configparser
import os,glob,sys

def loadConfig():
    """
    Load a configuration file from the default location
    
    Returns a configparser representation of the configuration file
    """    
    #Get list of ini files
    iniFile = glob.glob('*.ini')

    #Check that exactly one config file is present
    nIniFiles=len(iniFile)
    if(nIniFiles!=1):
        sys.exit('Exactly one config file must be defined in the root directory. Currently ' + str(nIniFiles) +' files are provided.')

    #Load the file
    thisCfg=configparser.ConfigParser()
    thisCfg.read(iniFile)
    
    #Finished
    return thisCfg

        