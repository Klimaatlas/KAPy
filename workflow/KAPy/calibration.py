"""
#Setup for debugging with VS code
import os
print(os.getcwd())
import KAPy
os.chdir("KAPy")
import helpers as helpers
os.chdir("../..")
config=KAPy.getConfig("./config/config.yaml")  
histSimFile='./results/1.variables/tas/tas_CORDEX_AFR-22_rcp85_MPI-M-MPI-ESM-LR_r1i1p1_CLMcom-KIT-CCLM5-0-15_v1_mon_AFR-22.nc'
refFile="./results/1.variables/tas/tas_ERA5_ERA5-grid_no-expt_t2m_ERA5_monthly.nc"
thisCal='tas-CAL'
%matplotlib qt
import matplotlib.pyplot as plt
"""

import xarray as xr
from cdo import Cdo
from . import helpers

def calibrate(config,histSimFile,refFile,outFile, thisCal):
    #Import when we need the function
#    import cmethods as cmethods
    from xclim import sdba 

    # We choose to follow here the Xclim typology of ref / hist / sim, with the
    # assumption that the hist and sim part are contained in the same file
    #Import files - enforce loading, to avoid dask issues
    histSimDat=helpers.readFile(histSimFile).compute()
    refDat=helpers.readFile(refFile).compute()
    calCfg=config['calibration'][thisCal]

    # Regrid calibration data to the refData set 
    # First a write a single time slice of the reference data out, to use as the 
    # grid descriptor for the reference data set, then regrid using
    # CDO nearest neighbour interpolation
    cdo=Cdo()
    refGriddes=cdo.seltimestep('1/1',input=refDat)
    histSimNNFname=cdo.remapnn(refGriddes,input=histSimDat)
    histSimNN=helpers.readFile(histSimNNFname,format=".nc").compute()

    #Truncate time slice to the common calibration period (CP). Ensure synchronisation
    #between times and grids using nearest neighbour interpolation of
    #the sim data to the obs data
    histNN=helpers.timeslice(histSimNN,
                     calCfg['calPeriodStart'],
                     calCfg['calPeriodEnd'])
    refDatCP=helpers.timeslice(refDat,
                     calCfg['calPeriodStart'],
                     calCfg['calPeriodEnd'])


    #Match calendars between observations and simulations
    #Note that here we have chosen here to align on year when converting to/from
    #a 360 day calendar. This follows the recommendation in the xarray documentaion,
    #under the assumption that we are primarily going to be working with daily data.
    #See here for details:
    #https://docs.xarray.dev/en/stable/generated/xarray.Dataset.convert_calendar.html
    histNN=histNN.convert_calendar(refDatCP.time.dt.calendar,
                                   use_cftime=True,
                                   align_on="year")                     

    #Setup mapping to methods
    cmethodsAdj={"cmethods-linear":'linear_scaling',
              "cmethods-variance":'variance_scaling',
              "cmethods-delta":"delta_method",
              "cmethods-quantile":'quantile_mapping',
              "cmethods-quantile-delta":'quantile_delta_mapping'}
    

    #Apply method
    # if calCfg['method'] in cmethodsAdj.keys():
    #     #Use the adjust function from python cmethods
    #     res=cmethods.adjust(method=cmethodsAdj[calCfg['method']],
    #                 obs=refDatCP,
    #                 simh=calThisNNCP,
    #                 simp=calThisNN,
    #                 **calCfg['additionalArgs'])

    # elif calCfg['method']=="cmethods-detrended":
    #     # Distribution methods from cmethods
    #     from cmethods.distribution import detrended_quantile_mapping
    #     ValueError('Shouldnt be here')

    if calCfg['method']=="xclim":
        #Empirical quantile mapping
        EQM = sdba.EmpiricalQuantileMapping.train(refDatCP, 
                                                 histNN, 
                                                 group="time."+calCfg['grouping'],
                                                 **calCfg['additionalArgs'])
        res = EQM.adjust(histSimNN, extrapolation="constant", interp="nearest")

        #Correct output
        res = res.transpose(*refDatCP.dims)

    else:
        #Custom defined function
        raise ValueError(f'Unsupported calibration method "{calCfg['method']}".')


    #Finished
    res.name=calCfg['outVariable']
    res.to_netcdf(outFile[0])


