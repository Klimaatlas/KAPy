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
        #Recursive update function - thanks to ChatGPT
        def recursive_update_dict(d, update_dict):
            for key, value in d.items():
                if isinstance(value, dict) and key in update_dict:
                    # If the value is another dictionary and the key exists in the update_dict,
                    # recursively update it with the corresponding update_dict entry.
                    recursive_update_dict(value, update_dict[key])
                elif key in update_dict:
                    # If the key exists in the update_dict, 
                    # update the value in the original dictionary.
                    d[key] = update_dict[key]                   
            return(d)
        rtn=recursive_update_dict(dft,cfg)
        return(rtn)
    else:
        return(cfg)

'''
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
        sys.exit('Cannot find configuration file: ' + iniFile)
        

    #Load the file
    thisCfg=configparser.ConfigParser()
    thisCfg.read(iniFile)
    
    #Finished
    return thisCfg
'''
        