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


def generateArealstats(config, inFile, outFile):
    # Generate statistics over an area by applying a polygon mask and averaging
    # Setup xarray
    thisDat = xr.open_dataset(inFile[0])

    # Perform masking
    # TODO

    # Average spatially
    spMean = thisDat.indicator.mean(dim=["Yc", "Xc"])  # (dim=["longitude", "latitude"])

    # Save files pandas
    dfOut = spMean.to_dataframe()
    dfOut["area"] = "All"  # Currently place holder. Implement masking in future.
    dfOut.to_csv(outFile[0])
