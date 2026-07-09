"""
#Setup for debugging with VSCode 
import os
print(os.getcwd())
import KAPy
os.chdir("../..")
config=KAPy.getConfig("./config/config.yaml")  
wf=KAPy.getWorkflow(config)
varID='e_sat'
inputVars=config['secondaryVars'][varID]['inputVars']
outputVars=config['secondaryVars'][varID]['outputVars']
processorType=config['secondaryVars'][varID]['processorType']
processorPath=config['secondaryVars'][varID]['processorPath']
processorFunction=config['secondaryVars'][varID]['processorFunction']
passXarrays=config['secondaryVars'][varID]['passXarrays']
additionalArgs=config['secondaryVars'][varID]['additionalArgs']
outFile=list(wf['secondaryVars'][thisID])[0]
inFiles=wf['secondaryVars'][thisID][outFile]
from KAPy import helpers 
"""

import xarray as xr
import importlib
import os
from . import helpers


def buildDerivedVar(inFiles, passXarrays, scriptPath, scriptFunction,
                    additionalArgs,**kwargs):

    # Load input files
    if passXarrays:  # Then load the paths into xarrays. Otherwise just pass the path.
        inFiles = {thisKey: helpers.readFile(thisPath) for thisKey, thisPath in inFiles.items()}

    # Now get the function to call
    thisFn=helpers.getExternalFunction(scriptPath,
                                        scriptFunction)
    #Check the signature
    try:
        helpers.checkSignature(thisFn, inFiles)
    except ValueError as e:
        raise ValueError(
            f"Error in the signature of the external function '{scriptFunction}' "
            f"in '{scriptPath}': {e}"
        ) from None            


    # Call function
    theseArgs = {**inFiles, **additionalArgs}
    out = thisFn(**theseArgs)

    #Check output
    if passXarrays:  # Then load the paths into xarrays. Otherwise just pass the path.
        if not isinstance(out,xr.DataArray):
            raise TypeError(f"When passXarrays is true, KAPy expects  {scriptPath} - {scriptFunction} to return  an xarray dataarray but actually recieved {type(out)}")
    else:
        if not isinstance(out,dict):
            raise TypeError(f"When passXarrays is false, KAPy expects  {scriptPath} - {scriptFunction} to return  a dict of paths to the output files but actually recieved {type(out)}")

    return out

