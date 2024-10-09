"""
#Setup for debugging with VS code
import os
os.chdir("..")
import KAPy
os.chdir("..")
config=KAPy.getConfig("./config/config.yaml")
inFile=['./results/1.variables/tas/tas_CORDEX_rcp85_AFR-44_MPI-M-MPI-ESM-LR_r1i1p1_SMHI-RCA4_v1_mon.nc']
inFile=["./results/1.variables/tas/tas_ERA5_t2m_ERA5_monthly.nc"]
indID='101'
"""

import xarray as xr
import numpy as np
import pandas as pd
import sys
from .helpers import readFile


def calculateIndicators(config, inFile, outFile, indID):

    # Retrieve indicator information
    thisInd = config["indicators"][indID]

    # Read the dataset object back from disk, depending on the configuration
    thisDat = readFile(inFile[0])

    # Filter by season first (should always work)
    theseMonths = config["seasons"][thisInd["season"]]["months"]
    datSeason = thisDat.sel(time=np.isin(thisDat.time.dt.month, theseMonths))

    # Time binning over periods
    if thisInd["time_binning"] == "periods":
        slices = []
        for thisPeriod in config["periods"].values():
            # Slice dataset
            timemin = datSeason.time.dt.year >= thisPeriod["start"]
            timemax = datSeason.time.dt.year <= thisPeriod["end"]
            datPeriodSeason = datSeason.sel(time=timemin & timemax)
            # timebounds = pd.to_datetime([f"{thisPeriod['start']}-01-01", f"{thisPeriod['end']}-12-31"])
            # timestamp = timebounds.mean()

            # If there is nothing left, we want a result all the same so that we
            # can put it in the outputs. We copy the structure and populate
            # it with NaNs
            if datPeriodSeason.time.size == 0:
                res = datSeason.isel(time=0)
                res.data[:] = np.nan
            # Apply the operator
            elif thisInd["statistic"] == "mean":
                res = datPeriodSeason.mean("time", keep_attrs=True)
            else:
                sys.exit(f"Unknown indicator statistic '{thisInd["statistic"]}'")
                # sys.exit('Unknown indicator statistic, "' + ind["statistic"] + '"')
            # Tidy output
            res["periodID"] = thisPeriod["id"]
            slices.append(res)

        # Convert list back into dataset
        dout = xr.concat(slices, dim="periodID", coords="minimal")
        dout.periodID.attrs["name"] = "periodID"
        dout.periodID.attrs["description"] = f"For period definitions see {config['configurationTables']['periods']}"

    # Time binning by defined units
    elif thisInd["time_binning"] in ["years", "months"]:
        # Then group by time
        if thisInd["time_binning"] == "years":
            datGroupped = datSeason.resample(time="1Y", label="right")
        elif thisInd["time_binning"] == "months":
            datGroupped = datSeason.resample(time="1M", label="right")
        else:
            sys.exit("Shouldn't be here")

        # Apply the operator
        if thisInd["statistic"] == "mean":
            dout = datGroupped.mean(["time"], keep_attrs=True)
        else:
            sys.exit('Unknown indicator statistic, "' + thisInd["statistic"] + '"')

        # Round time to the middle of the month. This ensures that everything
        # has an identical datetime, regardless of the calendar being used.
        # Kudpos to ChatGPT for this little work around
        dout["time"] = pd.to_datetime(dout.time.dt.strftime("%Y-%m-15"))

    else:
        sys.exit("Unknown time_binning method, '" + thisInd["time_binning"] + "'")

    # Polish final product
    dout.name = "indicator"
    dout.attrs = {}
    for thiskey in thisInd.keys():
        if thiskey != "files":
            dout.attrs[thiskey] = thisInd[thiskey]

    # Write out
    dout.to_netcdf(outFile[0])
