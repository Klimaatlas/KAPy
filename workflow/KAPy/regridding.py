"""
#Setup for debugging with a Jupyterlab console
import os
os.chdir("..")
import KAPy
os.chdir("..")
config=KAPy.getConfig("./config/config.yaml")  
inFile=["results/3.indicators/101_CORDEX_rcp26_AFR-22_MOHC-HadGEM2-ESr1i1p1_GERICS-REMO2015_v1_mon.nc"]
"""
import xarray as xr
import numpy as np
import sys
    
def regrid(config,inFile,outFile):
    # #Currently only works for 'xesmf' regridding. Potentially add CDO in the future
    # if not config['outputGrid']['regriddingEngine']=='xesmf':
    #     sys.exit("Regridding options are currently limited to xesmf. See documentation")
        
    #Load xarray object
    dsIn= xr.open_dataarray(inFile[0])
    
    #... and then some magic happens....
    dsOut=dsIn

    #Write out
    dsOut.to_netcdf(outFile[0])
