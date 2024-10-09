"""
#Setup for debugging with a Jupyterlab console
import os
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

    # Make dataset object. We do this manually, so as to explictly avoid
    # dask getting involved. This may change in the future
    # We also do the cutouts at this point, so as to minimise the amount of
    # data that is actually loaded into memory
    dsList = []
    for f in inFiles:
        if config["cutouts"]["method"] == "lonlatbox":
            # Do cutouts using cdo sellonlatbox
            cdo = Cdo()
            thisDs = cdo.sellonlatbox(
                config["cutouts"]["xmin"],
                config["cutouts"]["xmax"],
                config["cutouts"]["ymin"],
                config["cutouts"]["ymax"],
                input=f,
                returnXDataset=True,
            )
            # print(type(thisDs))
            # print(np.min(thisDs["lon"]))
            # print(np.max(thisDs["lon"]))
            # print(np.min(thisDs["lat"]))
            # print(np.max(thisDs["lat"]))
            dsList += [thisDs]
        elif config["cutouts"]["method"] == "none":
            # Load everything using xarray
            dsList += [xr.open_dataset(f)]
        else:
            sys.exit(f"Unsupported cutout option '{config['cutouts']['method']}'.")

    # Now combine into one object
    dsIn = xr.combine_by_coords(dsList, combine_attrs="drop_conflicts")

    # Select the desired variable and rename it
    ds = dsIn.rename({thisInp["internalVarName"]: thisInp["varName"]})
    da = ds[thisInp["varName"]]  # Convert to dataarray

    # Drop degenerate dimensions. If any remain, throw an error
    da = da.squeeze()
    if len(da.dims) != 3:
        sys.exit(
            f"Extra dimensions found in processing '{inpID}' - there should be only "
            + "three dimensions after degenerate dimensions are dropped but "
            + f"found {len(da.dims)} i.e. {da.dims}."
        )

    # Apply additional preprocessing scripts
    if thisInp["applyPreprocessor"]:
        thisSpec = importlib.util.spec_from_file_location("customScript", thisInp["preprocessorPath"])
        thisModule = importlib.util.module_from_spec(thisSpec)
        thisSpec.loader.exec_module(thisModule)
        ppFn = getattr(thisModule, thisInp["preprocessorFunction"])
        da = ppFn(da)  # Assume no input arguments

    # Write the dataset object to disk, depending on the configuration
    # Currently write the whole lot. Could potentially pickle in the future
    da.to_netcdf(outFile[0])
