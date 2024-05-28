"""
#Setup for debugging with a Jupyterlab console
import os
os.chdir("..")
import KAPy
os.chdir("..")
config=KAPy.getConfig("./config/config.yaml")  
inFile=["results/2.indicators/101/101_CORDEX_rcp85_AFR-44_NOAA-GFDL-GFDL-ESM2M_r1i1p1_SMHI-RCA4_v1_mon.nc"]
outFile=["results/3.common_grid/101/101_CORDEX_rcp85_AFR-22_MPI-M-MPI-ESM-LR_r1i1p1_GERICS-REMO2015_v1_mon.nc"]
inFile=["resources/ERA5_monthly/t2m_ERA5_monthly.nc"]
inFile=["/dmidata/users/shn/CORDEX_Ghana_extracted/tas_GHANA_AFR-44_MPI-M-MPI-ESM-LR_rcp85_r1i1p1_MPI-CSC-REMO2009_v1_mon_200601-201012.nc"]
outFile=["~/foo.nc"]
"""

from cdo import Cdo
import xarray as xr
import sys
from .helpers import readFile


def regrid(config, inFile, outFile):
    # Currently only works for 'cdo' regridding. Other engines such as xesmf could be supported in the future
    if not config["outputGrid"]["regriddingEngine"] == "cdo":
        sys.exit("Regridding options are currently limited to cdo. See documentation")

    # Setup CDO object
    cdo = Cdo()

    # We want to handle regridding slightly differently between time binning
    # based on periods and based on years / months - this is because CDO
    # doesn't like the idea of a periodID dimension. Start by opening
    # the file with xarray to figure out what we've got
    thisDat = readFile(inFile[0])

    # If we have time dimensions, then we can just do the regridding in one hit
    if "time" in thisDat.dims:
        # Apply regridding
        cdo.remapbil(
            config["outputGrid"]["cdoGriddes"], input=inFile[0], output=outFile[0]
        )

    # Otherwise if we have periodIDs dimensions, then we need to loop over the
    # periods manually
    elif "periodID" in thisDat.dims:
        periodSlices = []
        for thisPeriodID in thisDat.periodID.values:
            # Extract period slide
            thisPeriodDat = thisDat.sel(periodID=thisPeriodID)
            # Apply regridding back to an xarray
            regridded = cdo.remapbil(
                config["outputGrid"]["cdoGriddes"],
                input=thisPeriodDat,
                returnXDataset=True,
            )
            periodSlices += [regridded]

        # Concatenate results and (re)build output
        dout = xr.concat(periodSlices, dim="periodID")
        dout["periodID"] = thisDat.periodID

        # Finally, we need to write out manually
        dout.to_netcdf(outFile[0])

    # Otherwise, shouldn't be here
    else:
        sys.exit(f"Can't identify structure of input file : {inFile[0]}.")
