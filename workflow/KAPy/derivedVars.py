"""
#Setup for debugging with VSCode 
import os
print(os.getcwd())
import KAPy
os.chdir("../..")
config=KAPy.getConfig("./config/config.yaml")  
wf=KAPy.getWorkflow(config)
varID='e_sat'
input_variables=config['secondaryVars'][varID]['input_variables']
output_variables=config['secondaryVars'][varID]['output_variables']
processorType=config['secondaryVars'][varID]['processorType']
processorPath=config['secondaryVars'][varID]['processorPath']
processorFunction=config['secondaryVars'][varID]['processorFunction']
pass_xarrays=config['secondaryVars'][varID]['pass_xarrays']
additional_arguments=config['secondaryVars'][varID]['additional_arguments']
outFile=list(wf['secondaryVars'][thisID])[0]
inFiles=wf['secondaryVars'][thisID][outFile]
from KAPy import helpers 
"""

import xarray as xr
from . import helpers


def buildDerivedVar(
    inFiles,
    pass_xarrays,
    custom_script,
    custom_function,
    additional_arguments,
    **kwargs,
):

    # Load input files
    if pass_xarrays:  # Then load the paths into xarrays. Otherwise just pass the path.
        inFiles = {
            thisKey: helpers.readFile(thisPath) for thisKey, thisPath in inFiles.items()
        }

    # Now get the function to call
    thisFn = helpers.getExternalFunction(custom_script, custom_function)
    # Check the signature
    try:
        helpers.checkSignature(thisFn, inFiles)
    except ValueError as e:
        raise ValueError(
            f"Error in the signature of the external function '{custom_function}' "
            f"in '{custom_script}': {e}"
        ) from None

    # Call function
    theseArgs = {**inFiles, **additional_arguments}
    out = thisFn(**theseArgs)

    # Check output
    if pass_xarrays:  # Then load the paths into xarrays. Otherwise just pass the path.
        if not isinstance(out, xr.DataArray):
            raise TypeError(
                f"When pass_xarrays is true, KAPy expects  {custom_script} - {custom_function} to return  an xarray dataarray but actually recieved {type(out)}"
            )
    else:
        if not isinstance(out, dict):
            raise TypeError(
                f"When pass_xarrays is false, KAPy expects  {custom_script} - {custom_function} to return  a dict of paths to the output files but actually recieved {type(out)}"
            )

    return out
