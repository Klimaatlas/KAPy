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
    ds =xr.open_mfdataset(inFiles,
                 combine='nested',
                concat_dim='time')
    #Sort on time
    ds=ds.sortby('time')
    
    #Select the desired variable and rename it
    selVar=ds.rename({thisInp['internalVarName']:thisInp['varName']})
    selVar=selVar[thisInp['varName']]
    
    """
    #Reapply domain criteria here
        dsSel = ds.sel(lat=slice(config['domain']['ymin'], 
                          config['domain']['ymax']), 
                       lon=slice(config['domain']['xmin'], 
                          config['domain']['xmax']))
    """

    #Write the dataset object to disk, depending on the configuration
    if config['primVars']['storeAsNetCDF']:
        selVar.to_netcdf(outFile[0]) 
    else:
        with open(outFile[0],'wb') as f:
            pickle.dump(selVar,f,protocol=-1)

    
