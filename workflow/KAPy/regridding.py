"""
#Setup for debugging with a Jupyterlab console
import os
os.chdir("..")
import KAPy
os.chdir("..")
config=KAPy.loadConfig()  
inFile=["results/3.indicators/101_CORDEX_rcp26_AFR-22_MOHC-HadGEM2-ESr1i1p1_GERICS-REMO2015_v1_mon.nc"]
"""
import xarray as xr
import numpy as np
import xesmf as xe

    
def regrid(config,inFile,outFile):
    #Get output options
    outOpt=config['outputGrid']
    
    #Setup grid onto which regridding takes place
    outGrd = xr.Dataset(
    {
        outOpt['yname']: ([outOpt['yname']], 
                          np.arange(outOpt['ymin'],
                                   outOpt['ymax'],
                                   outOpt['dy']),
                {"units": outOpt['yunits']}),
        outOpt['xname']: ([outOpt['xname']], 
                          np.arange(outOpt['xmin'],
                                   outOpt['xmax'],
                                   outOpt['dx']),
                {"units": outOpt['xunits']})
    })
    
    #Setup xarray object
    dsIn= xr.open_dataarray(inFile[0])
    
    #Do the regridding
    regridder = xe.Regridder(dsIn, outGrd, 
                             method=outOpt['interpMethod'],
                             extrap_method=outOpt['extrapMethod'],
                             unmapped_to_nan=True)
    dsout=regridder(dsIn)
    
    #Write out
    dname=os.path.dirname(outFile[0])
    if not os.path.exists(dname):
        os.makedirs(dname)
    dsout.to_netcdf(outFile[0])
    

