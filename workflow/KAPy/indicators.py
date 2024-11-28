"""
#Setup for debugging with VS code
import os
print(os.getcwd())
import helpers as helpers
os.chdir("..")
import KAPy
os.chdir("..")
config=KAPy.getConfig("./config/config.yaml")  
wf=KAPy.getWorkflow(config)
indID='201'
outFile=[next(iter(wf['indicators'][indID]))]
inFile=wf['indicators'][indID][outFile[0]]
import matplotlib.pyplot as plt
%matplotlib qt

"""

import xarray as xr
import numpy as np
import pandas as pd
import sys
import cftime
from . import helpers 

def calculateIndicators(config, inFile, outFile, indID):

    # Retrieve indicator information
    thisInd = config["indicators"][indID]

    # Read the dataset object back from disk, depending on the configuration
    thisDat = helpers.readFile(inFile[0])

    # Filter by season first (should always work)
    theseMonths = config["seasons"][thisInd["season"]]["months"]
    datSeason = thisDat.sel(time=np.isin(thisDat.time.dt.month, theseMonths))

    # Time binning over periods
    if thisInd["time_binning"] == "periods":
        slices = []
        for thisPeriod in config["periods"].values():
            # Slice dataset
            datPeriodSeason=helpers.timeslice(datSeason,thisPeriod["start"],thisPeriod["end"])
            # If there is nothing left, we want a result all the same so that we
            # can put it in the outputs. We copy the structure and populate
            # it with NaNs
            if datPeriodSeason.time.size == 0:
                res = datSeason.isel(time=0)
                res=res.drop_vars("time")
                res.data[:] = np.nan
            # Else apply the operator
            elif thisInd["statistic"] == "mean":
                res = datPeriodSeason.mean("time", keep_attrs=True)
            else:
                sys.exit('Unknown indicator statistic, "' + ind["statistic"] + '"')
            # Tidy output
            res["periodID"] = thisPeriod["id"]
            slices.append(res)

        # Convert list back into dataset
        dout = xr.concat(slices, dim="periodID")
        dout.periodID.attrs["name"] = "periodID"
        dout.periodID.attrs["description"] = (
            f"For period definitions see {config['configurationTables']['periods']}"
        )

    # Time binning by defined units
    elif thisInd["time_binning"] in ["years", "months"]:
        # Then group by time. Could consider using groupby as an alternative
        if thisInd["time_binning"] == "years":
            datGroupped = datSeason.resample(time="YE", label="right")
        elif thisInd["time_binning"] == "months":
            datGroupped = datSeason.resample(time="ME", label="right")
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
        # Note that we need to ensure cftime representation, for runs that
        # go out paste 2262
        dout["time"] = [cftime.DatetimeGregorian(x.dt.strftime("%Y"),x.dt.strftime("%m"),15)
                                                for x in dout.time]

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
