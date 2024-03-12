"""
#Debug setup
import os
os.chdir("../..")
"""

import yaml
import pandas as pd
from snakemake.utils import validate
import os
import sys


def loadConfig(configfile='config.yaml'):
    '''
    Load config file
    
    Loads the KAPy config file specified in the yaml format.
    '''
    
    #Load config file
    with open(configfile, 'r') as f:
    	cfg=yaml.safe_load(f)
        
    #Validate configuration file
    validate(cfg,"./workflow/schemas/config.schema.json")

    #Now check that the other configuration tables exist
    for thisKey,thisPath in cfg['tables'].items():
        if not os.path.exists(thisPath):
            sys.exit(f"Cannot find configuration table '{thisKey}' at path '{thisPath}'.")
            
    #Validate each table in turn
    listCols={'indicators':[],
         'inputs':[],
         'scenarios':['experiments'],
         'periods':[],
         'seasons':['months']}
    for thisTblKey,theseCols in listCols.items():
        #Load the variables that are defined as tabular configurations
        #We allow some columns to be defined here as lists, but these need to be
        #parsed before we can actually use them for something
        thisTbl=pd.read_csv(cfg['tables'][thisTblKey],sep="\t",
                            converters={col: pd.eval for col in theseCols})
        #Validate against the appropriate schema.
        #Note that Snakemake doesn't validate arrays in tabular configurations at the moment
        # https://github.com/snakemake/snakemake/issues/2601
        #Drop months from the validation scheme
        if thisTblKey=="seasons":
            valThis=thisTbl.drop(columns=['months'])
        else:
            valThis=thisTbl
        validate(valThis, f"./workflow/schemas/{thisTblKey}.schema.json")
        #If there is an id column set it as the index so it can be used as the key
        if "id" in thisTbl.columns:
            thisTbl=thisTbl.set_index('id',drop=False)
        #Make dict
        cfg[thisTblKey]=thisTbl.to_dict(orient='index')
    
    ##TODO:
    #Indicators
        # Check that season ids are in the seasons table, or that all is chosen
        # Check that variables choices are valid
    #Throw validation error in an informative manner.
        
    
    
    return(cfg)

