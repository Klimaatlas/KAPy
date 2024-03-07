import os
import glob
import sys
from collections.abc import Iterable
import yaml
import pandas as pd
from ast import literal_eval

def loadConfig(configfile='config.yaml'):
    '''
    Load config file
    
    Loads the KAPy config file specified in the yaml format.
    '''
    
    #Load config file
    with open(configfile, 'r') as f:
    	cfg=yaml.safe_load(f)
        
    #Load the variables that are defined as tabular configurations
    #We allow some columns to be defined here as lists, but these need to be
    #parsed before we can actually use them for something
    listCols={'inputs':[],
         'indicators':[],
         'scenarios':['experiments'],
         'periods':[],
         'seasons':['months']}
    for thisTblKey,theseCols in listCols.items():
        thisTbl=pd.read_csv(cfg[thisTblKey],sep="\t",
                            converters={col: literal_eval for col in theseCols})
        #If there is an id column set it as the index so it can be used as the key
        if "id" in thisTbl.columns:
            thisTbl=thisTbl.set_index('id',drop=False)
        #Make dict
        cfg[thisTblKey]=thisTbl.to_dict(orient='index')
    
    return(cfg)

