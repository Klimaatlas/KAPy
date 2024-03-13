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


def loadConfig(configfiles=['./config.yaml','./config/config.yaml']):
    '''
    Load config file
    
    Loads the KAPy config file specified in the yaml format. The script loops
    through the list of files until a file is found
    '''
    
    #Find existing files
    foundCfg=False
    for cfgFile in configfiles:
        if os.path.exists(cfgFile):
            with open(cfgFile, 'r') as f:
                cfg=yaml.safe_load(f)
            foundCfg=True
            break
    if not foundCfg:
        sys.exit(f"Cannot find a configuration file in: {configfiles}")
        
    #Validate configuration file
    validate(cfg,"./workflow/schemas/config.schema.json")

    #Now check that the other configuration tables exist
    for thisKey,thisPath in cfg['configurationTables'].items():
        if not os.path.exists(thisPath):
            sys.exit(f"Cannot find configuration table '{thisKey}' at path '{thisPath}'.")
            
    #Validate each table in turn
    listCols={'indicators':[],
         'inputs':[],
         'scenarios':[],
         'periods':[],
         'seasons':['months']}
    for thisTblKey,theseCols in listCols.items():
        #Load the variables that are defined as tabular configurations
        thisTbl=pd.read_csv(cfg['configurationTables'][thisTblKey],sep="\t")
        #We allow some columns to be defined here as lists, but these need to be
        #parsed before we can actually use them for something
        for col in theseCols:
            thisTbl[col]=thisTbl[col].str.split(",")
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
    
    #Manual validation -----------------
    #Some things are a bit tricky to validate with JSON schemas alone, particular where
    #we have validations that cross schemes. The following checks are therefore done
    #manually.
    #Firstly, We need to validate the months part of the seasons table manually.
    for thisKey,theseValues in cfg['seasons'].items():
        theseMnths=theseValues['months']
        if len(theseMnths) > 12:
            sys.exit("Between 1 and 12 months should be selected")
        if len(theseMnths) == 0: #Set to all months
            theseMnths=list(range(1,13))
        #Length is ok. Now convert to integers
        theseMnths=[int(i) for i in theseMnths]
        if max(theseMnths)>12 | min(theseMnths)<1:
            sys.exit("Month specification must be between 1 and 12 inclusive")
        #Write the integers back to finish
        cfg['seasons'][thisKey]['months']=theseMnths

    #Season selected in the indicator table must be valid
    #Currently allow only one season per indicator. This needs to be fixed in the future
    indTbl=pd.DataFrame.from_dict(cfg['indicators'],orient='index')
    validSeasons=list(cfg['seasons'].keys()) + ['all']
    for seasonRequest in indTbl['season']:
        if not(all([this in validSeasons for this in [seasonRequest]])):
            sys.exit(f"Unknown season specified in: {seasonRequest}")
            
    return(cfg)

