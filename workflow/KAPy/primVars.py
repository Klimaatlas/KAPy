"""
#Setup for debugging with a Jupyterlab console
import os
print(os.getcwd())
os.chdir("..")
import KAPy
os.chdir("..")
config=KAPy.getConfig("./config/config.yaml")  
wf=KAPy.getWorkflow(config)
inpID=next(iter(wf['primVars'].keys()))
outFile=[next(iter(wf['primVars'][inpID]))]
inFiles=wf['primVars'][inpID][outFile[0]]

"""

# Given a set of input files, create objects that can be worked with
import xarray as xr
import pickle
import sys
import importlib
from cdo import Cdo


def buildPrimVar(config, inFiles, outFile, inpID):
    """
    Build the data object

    Build the set of input files into a single xarray-based dataset object
    and write it out, either as a NetCDF file or as a pickle.
    """
    # Get input configuration
    thisInp = config["inputs"][inpID]

    # Make dataset object using xarray lazy load approach.
    dsIn =xr.open_mfdataset(inFiles,
                            combine='nested',
                            concat_dim='time')

    # Select the desired variable and rename it
    ds = dsIn.rename({thisInp["internalVarName"]: thisInp["varID"]})
    da = ds[thisInp["varID"]]  # Convert to dataarray

    # Drop degenerate dimensions. If any remain, throw an error
    da = da.squeeze()
    if len(da.dims) != 3:
        sys.exit(
            f"Extra dimensions found in processing '{inpID}' - there should be only "
            + f"three dimensions after degenerate dimensions are dropped but "
            + f"found {len(da.dims)} i.e. {da.dims}."
        )

    #Apply cutout functionality
    if config["cutouts"]["method"] == "lonlatbox":
        # The processing chain here is to first take
        # a slide, and then do a cdo cutoout on it. This
        # can be used as a mask on the xarray object - this
        # way we can maintain the lazy-loading and storage benefits
        # associated with pickling
        
        # Extract first time step. This avoids having to work
        # with the entire dataset
        firstTS=da.isel(time=0)

        # Do cutouts using cdo sellonlatbox.
        cdo = Cdo()
        cutoutMask = cdo.sellonlatbox(
            config["cutouts"]["xmin"],
            config["cutouts"]["xmax"],
            config["cutouts"]["ymin"],
            config["cutouts"]["ymax"],
            input=firstTS,
            returnXDataset=True)
        
        # Apply masking to data array object
        da=da.where(cutoutMask.notnull(),drop=True)

    elif config["cutouts"]["method"] != "none":
        #problem
        sys.exit(f"Unsupported cutout option '{config['cutouts']['method']}'.")

    # # Apply additional preprocessing scripts
    # if thisInp["importScriptPath"]!='':
    #     thisSpec = importlib.util.spec_from_file_location(
    #         "customScript", thisInp["importScriptPath"]
    #     )
    #     thisModule = importlib.util.module_from_spec(thisSpec)
    #     thisSpec.loader.exec_module(thisModule)
    #     ppFn = getattr(thisModule, thisInp["importScriptFunction"])
    #     da = ppFn(da)  # Assume no input arguments

    # Write the dataset object to disk, depending on the configuration
    if config['processing']['picklePrimaryVariables']:
        with open(outFile[0],'wb') as f:
            pickle.dump(da,f,protocol=-1)
    else:
        da.to_netcdf(outFile[0])
