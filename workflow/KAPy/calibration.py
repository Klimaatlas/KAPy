"""
#Setup for debugging with VS code
import os
print(os.getcwd())
import KAPy
os.chdir("..")
config=KAPy.getConfig("./config/config.yaml")  
calibrateThis=['./results/1.variables/tas/tas_CORDEX_AFR-44_rcp85_NCC-NorESM1-M_r1i1p1_SMHI-RCA4_v1_mon_AFR-44.nc.pkl']
refFile=["./results/1.variables/tas/tas_ERA5_ERA5-grid_no-expt_t2m_ERA5_monthly.nc.pkl"]
refFile=["./results/1.variables/tas/tas_ERA5_ERA5-grid_no-expt_era5_tmax.nc.pkl"]
thisCal='tas'
%matplotlib inline
import matplotlib.pyplot as plt
"""

# TODO: We have a good framework here but it needs to be generalised 
# quite a bit as well. Adding a grid metadata table could be a good idea here
# There also seems to be a problem with the calendar for the test file, at least
# in part.

import xarray as xr
from . import helpers
from cdo import Cdo

def calibrate(config,calibrateThis,refFile,outFile, thisCal) {
    #Import files - enforce loading, to avoid dask issues
    simDat=readFile(calibrateThis[0]).compute()
    obsDat=readFile(refFile[0]).compute()
    calCfg=config['calibration'][thisCal]

    #Truncate time slice to a common period. Ensure synchronisation
    #between times and grids using nearest neighbour interpolation of
    #the sim data to the obs data
    calObs=timeslice(obsDat,
                     calCfg['calPeriodStart'],
                     calCfg['calPeriodEnd'])
    calSim=timeslice(simDat,
                     calCfg['calPeriodStart'],
                     calCfg['calPeriodEnd'])

    #Match calendars between observations and simulations
    calSim=calSim.convert_calendar(calObs.time.dt.calendar)                     
    calSim=calSim.interp(time=calObs['time'],method='nearest')

    #If the time dimensions for the calibration period are the same length
    #and cover the same timespace, it is a reasonable enough assumption that
    #they also represent the same values - hence a direct copy of one to the other
    #is probably ok. This may break down at some point though so check it
    # if calSim.time.size==calObs.time.size:
    #     calSim['time']=calObs.time
    # else:
    #     ValueError('Cannot match calendars between observations and simulations.')

    #Manually align dimension naming
    #If this works, we should probably define some grid metadata
    calObs=calObs.rename({'longitude':'x','latitude':'y'})
    calObs=calObs.drop_vars(['expver'])
    calSim=calSim.rename({'rlon':'x','rlat':'y'})
    calSim=calSim.drop_vars(['lon','lat','expver','height'])
    simDat=simDat.rename({'rlon':'x','rlat':'y'})
    simDat=simDat.drop_vars(['lon','lat','height'])

    #Now apply nearest-neighbour regridding, so that there is a 
    #spatial match
    calSim=calSim.interp_like(calObs,method='nearest')
    simDat=simDat.interp(x=calObs.x,y=calObs.y,method='nearest')

    #Setup mapping to methods
    cmethodsAdj={"cmethods-linear":'linear_scaling',
              "cmethods-variance":'variance_scaling',
              "cmethods-delta":"delta_method",
              "cmethods-quantile":'quantile_mapping',
              "cmethods-quantile-delta":'quantile_delta_mapping'}

    #Apply method
    if calCfg['method'] in cmethodsAdj.keys():
        #Use the adjust function from python cmethods
        from cmethods import adjust
        res=adjust(method=cmethodsAdj[calCfg['method']],
                    obs=calObs,
                    simh=calSim,
                    simp=simDat,
                    **calCfg['additionalArgs'])

    elif calCfg['method']=="cmethods-detrended":
        # Distribution methods from cmethods
        from cmethods.distribution import detrended_quantile_mapping
        ValueError('Shouldnt be here')

    elif calCfg['method']=="custom":
        #Custom defined function
        ValueError('Shouldnt be here')


    #Finished
    res.to_netcdf(outFile[0])

}



import xarray as xr
import cftime
import pandas as pd

# Create two datasets with different time calendars
# Dataset 1: Gregorian calendar (standard)
time_gregorian = pd.date_range("2000-01-01", periods=10, freq="ME")
ds1 = xr.Dataset(
    {
        "var1": ("time", range(10))
    },
    coords={
        "time": time_gregorian
    }
)

# Dataset 2: 360-day calendar (non-standard)
time_360_day = xr.cftime_range("2000-01-01", periods=8, freq="360D", calendar="360_day")
ds2 = xr.Dataset(
    {
        "var2": ("time", range(8))
    },
    coords={
        "time": time_360_day
    }
)

# Interpolate ds2 onto ds1's time axis using nearest-neighbor interpolation
# Ensure that 'method' is set to 'nearest'
ds2_interp = ds2.interp(time=ds1["time"], method="nearest")

print(ds2_interp)