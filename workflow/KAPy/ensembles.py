"""
#Setup for debugging with VS code
import os
os.chdir("..")
import KAPy
os.chdir("..")
config=KAPy.getConfig("./config/config.yaml")
wf=KAPy.getWorkflow(config)
ensID=next(iter(wf['ensstats'].keys()))
inFiles=wf['ensstats'][ensID]
"""

import xarray as xr
import xclim.ensembles as xcEns


def generateEnsstats(config, inFiles, outFile):
    # Setup the ensemble
    # Given that all input files have been regridded onto a common grid,
    # they can then be concatenated into a single object. There are
    # two approachs. Previously we have used the create_ensemble from xclim.ensembles
    # However, this is quite fancy, and does a lot of logic about calendars that
    # create further problems. Instead, given that everything is on the same grid,
    # we can just open it all using open_mfdataset
    # print(inFiles)
    thisEns = xr.open_mfdataset(inFiles, concat_dim="realization", combine="nested")
    # Calculate the statistics
    ens_mean_std = xcEns.ensemble_mean_std_max_min(thisEns)
    ens_percs = xcEns.ensemble_percentiles(
        thisEns, split=False, values=[float(x) for x in config["ensembles"].values()]
    )
    ensOut = xr.merge([ens_mean_std, ens_percs])
    # ensOut["periodID"].astype(float)

    # Write results
    ensOut.to_netcdf(outFile[0])
