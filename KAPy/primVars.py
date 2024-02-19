#Given a set of input files, create objects that can be worked with

import KAPy
import pandas as pd
import os
import xarray as xr
import pickle
import numpy as np
import sys
import glob
import re

#config=KAPy.loadConfig()  


def buildPrimVar(config,inFiles,outFile):
    """
    Build the data object
    
    Build the set of input files into a single xarray-based dataset object
    and write it out, either as a NetCDF file or as a pickle.
    """
    #Make dataset object, sorted on time
    ds =xr.open_mfdataset(inFiles,
                 combine='nested',
                concat_dim='time')
    ds=ds.sortby('time')
    
    """
    #Reapply domain criteria here
        dsSel = ds.sel(lat=slice(config['domain']['ymin'], 
                          config['domain']['ymax']), 
                       lon=slice(config['domain']['xmin'], 
                          config['domain']['xmax']))
    """

    #Write the dataset object to disk, depending on the configuration
    if config['primVars']['storeAsNetCDF']:
        ds.to_netcdf(outFile[0]) 
    else:
        with open(outFile[0],'wb') as f:
            pickle.dump(ds,f,protocol=-1)

    
