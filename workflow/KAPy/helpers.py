"""
import os
os.chdir("..")
os.chdir("..")
thisPath='outputs/1.primVars/pr_KA-ba_rcp26_EUR-11_CCCma-CanESM2r1i1p1_CLMcom-CCLM4-8-17_v1_day_19510101-20051231_DENMARK.pkl'
"""

import pickle
import xarray as xr
import os


def readFile(thisPath):
    # Reads a dataset from disk, determining dynmaically whether it is
    # pickled or NetCDF based on the file extension
    inExt = os.path.splitext(os.path.basename(thisPath))[1]
    if inExt == ".nc":
        thisDat = xr.open_dataarray(thisPath)
    elif inExt == ".pkl":  # Read pickle
        with open(thisPath, "rb") as f:
            thisDat = pickle.load(f)
    else:
        raise IOError(f"Unknown file format, {inExt} in {thisPath}")
    return thisDat


def timeslice(this,startYr,endYr):
    # Slice dataset
    timemin = this.time.dt.year >= int(startYr)
    timemax = this.time.dt.year <= int(endYr)
    sliced = this.sel(time=timemin & timemax)
    return sliced
