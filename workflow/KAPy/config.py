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
import ast


def readConfig(configfile):
    '''
    Read config file
    
    Reads the KAPy config master file specified in the yaml format. 
    '''
    #Load file
    if os.path.exists(configfile):
        with open(configfile, 'r') as f:
            cfg=yaml.safe_load(f)
    else:
        sys.exit(f"Cannot find configuration file: {configfile}. " + \
             "Working directory: '{os.getcwd()}'")
    return(cfg)
            
            

def validateConfig(config):
    '''
    Inflate and validate config file
    
    Validates a loaded configuration (i.e. read directly from the KAPy config master
    file), inflates it by loading the configuration tables, and validates all elements
    against the appropriate validation schema. Returns the inflated validated config.
    '''
    #Setup location of validation schemas
    #schemaDir="./workflow/schemas/"
    #schemaDir="./KAPy/workflow/schemas/"
    schemaDir=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","schemas")

    #Validate configuration file
    validate(config,os.path.join(schemaDir,"config.schema.json"))

    #Now check that the other configuration tables exist
    for thisKey,thisPath in config['configurationTables'].items():
        if not os.path.exists(thisPath):
            sys.exit(f"Cannot find configuration table '{thisKey}' at path '{thisPath}'.")

    #Now check that notebooks exist
    if isinstance(config['notebooks'],str):
        notebookPaths=[config['notebooks']]
    else:
        notebookPaths=config['notebooks']
    for thisPath in notebookPaths:
        if not os.path.exists(thisPath):
            sys.exit(f"Cannot find notebook '{thisPath}'.")
            
    #Validate each table in turn. The validation approach used
    #is defined in the following table
    tabularCfg={'indicators':{'listCols':[],
                              'dicts':[],
                              'schema':'indicators'},
         'inputs':{'listCols':[],
                   'dicts':[],
                   'schema':'inputs'},
         'scenarios':{'listCols':['scenarioStrings'],
                      'dicts':[],
                      'schema':'scenarios'},
         'periods':{'listCols':[],
                    'dicts':[],
                    'schema':'periods'},
         'seasons':{'listCols':['months'],
                     'dicts':[],
                     'schema':'seasons'},
         'secondaryVars':{'listCols':['inputVars','outputVars'],
                     'dicts':['additionalArgs'],
                     'schema':'derivedVars'}}
    for thisTblKey,theseVals in tabularCfg.items():
        #Load the variables that are defined as tabular configurations (if they exist)
        if not thisTblKey in config['configurationTables']:
            break
        thisCfgFile=config['configurationTables'][thisTblKey]
        thisTbl=pd.read_csv(thisCfgFile,sep="\t",comment="#")
        #We allow some columns to be defined here as lists, but these need to be
        #parsed before we can actually use them for something
        for col in theseVals['listCols']:
            thisTbl[col]=thisTbl[col].str.split(",")
        #Note that Snakemake doesn't validate arrays in tabular configurations at the moment
        # https://github.com/snakemake/snakemake/issues/2601
        #We therefore need to drop the list columns from the validation scheme
        valThis=thisTbl.drop(columns=theseVals['listCols'])
        #Validate against the appropriate schema.
        validate(valThis, os.path.join(schemaDir,f"{theseVals['schema']}.schema.json"))
        #Dict columns also need to be parsed
        for col in theseVals['dicts']:
            try:
                thisTbl[col]=[ast.literal_eval(x) for x in thisTbl[col]]
            except (SyntaxError, ValueError) as e:
                print(f"Error occurred in parsing column '{col}' in '{thisCfgFile}' : {e}")
                sys.exit()
        #Force id column to be a string. Set to as the index so it can be used as the key
        thisTbl['id']=[str(x) for x in thisTbl['id']]
        thisTbl=thisTbl.set_index('id',drop=False)
        #Make dict
        config[thisTblKey]=thisTbl.to_dict(orient='index')
    
    #Manual validation -----------------
    #Some things are a bit tricky to validate with JSON schemas alone, particular where
    #we have validations that cross schemes. The following checks are therefore done
    #manually.
    #Firstly, We need to validate the months part of the seasons table manually.
    for thisKey,theseValues in config['seasons'].items():
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
        config['seasons'][thisKey]['months']=theseMnths

    #Season selected in the indicator table must be valid
    #Currently allow only one season per indicator. This needs to be fixed in the future
    indTbl=pd.DataFrame.from_dict(config['indicators'],orient='index')
    validSeasons=list(config['seasons'].keys()) + ['all']
    for seasonRequest in indTbl['season']:
        if not(all([this in validSeasons for this in [seasonRequest]])):
            sys.exit(f"Unknown season specified in: {seasonRequest}")
            
    return(config)

def getConfig(configfile):
    '''
    Load and validate config file
    
    Reads the KAPy config master file specified in the yaml format using readConfig()
    and then validates it using validateConfig()
    '''
    cfg=readConfig(configfile)
    cfg=validateConfig(cfg)
    return(cfg)
