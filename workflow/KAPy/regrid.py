import xarray as xr
from cdo import Cdo
import numpy as np
import scipy as sp
import xesmf as xe


"""
#Setup for debugging with a Jupyterlab console
import os
print(os.getcwd())
import helpers
os.chdir("..")
import KAPy
os.chdir("../..")
config=KAPy.get_config("./config/config.yaml")  
wf=KAPy.get_workflow(config)
output_file=[list(wf['regrid']['input_dict'].keys())[0]]
input_path=[wf['regrid']['input_dict'][output_file[0]]['input_path']]
templateType=config['output_grid']['templateType']
path=config['output_grid']['path']
method=config['output_grid']['method']
tempDir=config['dirs']['tempDir']
%matplotlib inline
"""


def regrid(input_path, templateType, path, method, tempDir):
    # Check regridding approach is valid
    if templateType not in ["file", "cdo"]:
        raise ValueError(
            "Regridding options are currently limited to `file` or `cdo`. See documentation"
        )

    # Setup input files
    # ------------------
    # Note that as this is an indicator file, we open it as a dataset and load it
    # directly into RAM - no need for chunking here.
    # Explicitly tell xarray not to think about time here, for indicators that
    # give the units as number of days
    time_coder = xr.coders.CFDatetimeCoder(use_cftime=True)
    thisDat = xr.open_dataset(
        input_path[0], decode_times=time_coder, decode_timedelta=False
    )
    # Identify time coordinate
    if "time" in thisDat.dims:
        tCoord = "time"
    elif "periodID" in thisDat.dims:
        tCoord = "periodID"
    else:
        raise ValueError(
            f'Cannot find time or periodID coordinate in "{input_path[0]}".'
        )

    # Fill in the NaNs before regridding, to avoid bleeding from the surroundings
    # This is a bit work - we use scipy's griddata routine for regridding
    # of irregular data, as there is not really anything corresponding in xarray unfortunately.
    # This is only necessary though if there are NaNs in the file in the first place
    if np.isnan(thisDat.indicator).any().values | np.isnan(thisDat.delta).any().values:
        for var in ["indicator", "delta"]:
            for tID in np.arange(thisDat[tCoord].size):
                for sID in np.arange(thisDat.seasonID.size):
                    # Extract data. Skip if all NaNs
                    d = thisDat[var].isel({tCoord: tID, "seasonID": sID})
                    if d.isnull().all().values:
                        continue
                    # Extract non-nan values
                    dDf = d.to_dataframe()
                    valuesDf = dDf[~np.isnan(dDf[var])]
                    # Perform interpolation / extrapolation
                    xVals = d[d.dims[1]].values
                    yVals = d[d.dims[0]].values
                    yGrd, xGrd = np.meshgrid(yVals, xVals, indexing="ij")
                    grd = sp.interpolate.griddata(
                        np.array(valuesDf.index.to_list()),
                        valuesDf[var].to_numpy(),
                        (yGrd, xGrd),
                        method="nearest",
                    )
                    thisDat[var].values[tID, sID] = grd

    # Setup the reference grid, either by importing the file, or generating it with CDO
    if templateType == "file":
        # Import reference file directly
        refGrd = xr.open_dataarray(path)
    else:
        # Use the CDO griddes to make one
        cdo = Cdo(tempdir=tempDir)
        refGrd = cdo.const(42, path, returnXArray="const")

    # Apply regriddinng
    # ------------------
    # Note that the unmapped_to_nan can be a bit problematic, and caused segmentation faults
    # in xESMF v0.8.8. This should be fixed in v0.8.10.
    regrdr = xe.Regridder(thisDat, refGrd, method=method, unmapped_to_nan=True)

    # Do regridding
    regrdded = regrdr(thisDat, keep_attrs=True)

    # Mask output
    out = regrdded.where(~np.isnan(refGrd), np.nan)

    # Done
    return out
