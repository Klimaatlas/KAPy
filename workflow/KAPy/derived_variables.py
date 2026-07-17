"""
#Setup for debugging with VSCode 
import os
print(os.getcwd())
import KAPy
os.chdir("../..")
config=KAPy.get_config("./config/config.yaml")  
wf=KAPy.get_workflow(config)
varID='e_sat'
input_variables=config['secondaryVars'][varID]['input_variables']
output_variables=config['secondaryVars'][varID]['output_variables']
processorType=config['secondaryVars'][varID]['processorType']
processorPath=config['secondaryVars'][varID]['processorPath']
processorFunction=config['secondaryVars'][varID]['processorFunction']
pass_xarrays=config['secondaryVars'][varID]['pass_xarrays']
additional_arguments=config['secondaryVars'][varID]['additional_arguments']
output_file=list(wf['secondaryVars'][thisID])[0]
input_files=wf['secondaryVars'][thisID][output_file]
from KAPy import helpers 
"""

import xarray as xr

# Use absolute imports assuming KAPy is installed
from KAPy import helpers


def build_derived_variables(
    input_files,
    pass_xarrays,
    custom_script,
    custom_function,
    additional_arguments,
    **kwargs,
):

    # Load input files
    if pass_xarrays:  # Then load the paths into xarrays. Otherwise just pass the path.
        input_files = {
            thisKey: helpers.read_file(thisPath)
            for thisKey, thisPath in input_files.items()
        }

    # Now get the function to call
    thisFn = helpers.get_external_function(custom_script, custom_function)
    # Check the signature
    try:
        helpers.check_signature(thisFn, input_files)
    except ValueError as e:
        raise ValueError(
            f"Error in the signature of the external function '{custom_function}' "
            f"in '{custom_script}': {e}"
        ) from None

    # Call function
    theseArgs = {**input_files, **additional_arguments}
    out = thisFn(**theseArgs)

    # Output can be
    # 1. An xarray dataarray or dataset
    # 2. A dict of paths to files
    # indepdendent of the value of pass_xarrays
    if not (isinstance(out, xr.DataArray) | isinstance(out, xr.Dataset)| isinstance(out, dict)):
        raise TypeError(
            f"KAPy expects  {custom_script} - {custom_function} to return a dict of paths (strings), a dict of dataarrays, a single dataarray or a single dataset but received {type(out)}.")
    if isinstance(out, dict):
        #Check contents
        all_dataarrays=all(isinstance(v, xr.DataArray) for v in out.values())
        all_strings=all(isinstance(v, str) for v in out.values())
        #Can be either a dict of strings or a dict of xarrays
        if not (all_dataarrays | all_strings):
            out_types={k:type(v) for k,v in out.items()}
            raise TypeError(
                f"KAPy expects  {custom_script} - {custom_function} to return a dict of paths (strings), a dict of dataarrays, a single dataarray or a single dataset but one or more values in the dict is not satisfied: {out_types}."
            )
        

    return out
