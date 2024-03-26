"""
#Setup for debugging with a Jupyterlab console
import os
os.chdir("..")
import KAPy
os.chdir("..")
config=KAPy.loadConfig()  
wf=KAPy.getWorkflow(config)
thisID='SPI3'
thisVar=config['secondaryVars'][thisID]
inFiles=['./outputs/1.variables/pr/pr_KAba_rcp26_EUR-11_CCCma-CanESM2r1i1p1_CLMcom-CCLM4-8-17_v1_day.nc']
import sys
sys.path.append("KAPy/workflow/KAPy/")
from helpers import readFile
"""

import xarray as xr
import importlib
from .helpers import readFile
import os

def buildDerivedVar(config,inFiles,outFile,thisVar):
    
    #Build the input list into a dict
    inDict={os.path.basename(os.path.dirname(f)):f for f in inFiles}

    #Load input files
    if thisVar['passXarrays']:  #Then load the paths into xarrays. Otherwise just pass the path.
        inDict={thisKey : readFile(thisPath) for thisKey,thisPath in inDict.items()}
    
    #Now get the function to call
    if thisVar['processorType']=='module':
        thisModule=importlib.import_module(thisVar['processorPath'])
        thisFn=getattr(thisModule,thisVar['processorFunction'])
    elif thisVar['processorType']=='script':
        thisSpec=importlib.util.spec_from_file_location('customScript',thisVar['processorPath'])
        thisModule=importlib.util.module_from_spec(thisSpec)
        thisSpec.loader.exec_module(thisModule)
        thisFn=getattr(thisModule,thisVar['processorFunction'])
    else:
        sys.exit("Shouldn't be here")
    
    #Call function
    theseArgs={**inDict,**thisVar['additionalArgs']}
    out=thisFn(**theseArgs)
    
    #Write the results to disk
    out.name=thisVar['id']
    out.to_netcdf(outFile[0]) 

    
