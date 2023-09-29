import yaml

def loadConfig(configfile='config.yaml'):
    '''
    Load config file
    
    Loads the snakemake config file for help with debugging
    '''
    with open(configfile, 'r') as f:
        return(yaml.safe_load(f))