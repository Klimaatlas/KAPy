"""
#Setup for debugging with a Jupyterlab console
import os
os.chdir("..")
import KAPy
os.chdir("..")
config=KAPy.loadConfig()  
inFiles={'pr':'results/1.primVars/pr_CORDEX_rcp26_AFR-22_NCC-NorESM1-Mr1i1p1_GERICS-REMO2015_v1_mon.nc'}
thisVar=config['secondaryVars']['SPI3']
"""

import xarray as xr
import importlib

def buildDerivedVar(config,inFiles,outFile,thisVar):
    
    #Load input files
    if thisVar['passXarrays']:  #Then load the paths into xarrays. Otherwise just pass the path.
        inFiles={thisKey : xr.open_dataarray(thisPath) for thisKey,thisPath in inFiles.items()}
    
    #Now get the function to call
    if thisVar['srcType']=='module':
        thisModule=importlib.import_module(thisVar['srcPath'])
        thisFn=getattr(thisModule,thisVar['srcName'])
    elif thisVar['srcType']=='script':
        thisSpec=importlib.util.spec_from_file_location('customScript',thisVar['srcPath'])
        thisModule=importlib.util.module_from_spec(thisSpec)
        thisSpec.loader.exec_module(thisModule)
        thisFn=getattr(thisModule,thisVar['srcName'])
    else:
        sys.exit("Shouldn't be here")
    
    #Call function
    theseArgs={**inFiles,**thisVar['additionalArgs']}
    out=thisFn(**theseArgs)
    
    #Write the results to disk
    out.name=thisVar['name']
    out.to_netcdf(outFile[0]) 

    
