"""
#Setup for debugging with a Jupyterlab console
import os
os.chdir("..")
import KAPy
os.chdir("..")
config=KAPy.loadConfig()  
inFiles=['resources/ERA5_monthly/t2m_ERA5_monthly.nc']
inpID='ERA5-tas'
"""

#Given a set of input files, create objects that can be worked with
import xarray as xr
import pickle
import sys

#config=KAPy.loadConfig()  


def buildPrimVar(config,inFiles,outFile,inpID):
    """
    Build the data object
    
    Build the set of input files into a single xarray-based dataset object
    and write it out, either as a NetCDF file or as a pickle.
    """
    #Get input configuration
    thisInp=config['inputs'][inpID]
    
    #Make dataset object
    dsIn =xr.open_mfdataset(inFiles,
                 combine='nested',
                concat_dim='time')
    #Sort on time
    ds=dsIn.sortby('time')
    
    #Select the desired variable and rename it
    ds=ds.rename({thisInp['internalVarName']:thisInp['varName']})
    ds=ds[thisInp['varName']] #Convert to dataarray
    
    #Drop degenerate dimensions. If any remain, throw an error
    ds=ds.squeeze()
    if len(ds.dims)!=3:
        sys.exit(f"Extra dimensions found in processing '{inpID}' - there should be only " +\
                 f"three dimensions after degenerate dimensions are dropped but "+\
                 f"found {len(ds.dims)} i.e. {ds.dims}.")
   
    #Write the dataset object to disk, depending on the configuration
    if config['primVars']['storeAsNetCDF']:
        ds.to_netcdf(outFile[0]) 
    else:
        with open(outFile[0],'wb') as f:
            pickle.dump(ds,f,protocol=-1)

    
