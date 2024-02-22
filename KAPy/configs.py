""" Configuration management """

import yaml

def loadConfig(configfile='config.yaml',useDefaults=True,defaultFile='configs/defaults.yaml'):
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

