import KAPy
import pandas as pd
import os
import xarray as xr
import xclim
import xclim.ensembles as xcEns
import xesmf as xe
import pickle
import numpy as np
import tqdm
import sys
import glob
import re

#config=KAPy.loadConfig()  


def generateEnsstats(config,infiles,outfile):
    #Setup the ensemble
    #Enforce a join='override' to handle differences between grids close to
    #numerical precision
    thisEns = xcEns.create_ensemble(infiles,multifile=True,join='override')  
    #Calculate the statistics
    ens_mean_std = xcEns.ensemble_mean_std_max_min(thisEns)
    ens_percs = xcEns.ensemble_percentiles(thisEns, values=config['ensembles']['percentiles'])
    ensOut=xr.merge([ens_mean_std,ens_percs])
    #Write results
    ensOut.to_netcdf(outfile[0])
    
    
    
def regrid(config,inFile,outFile,):
    #Setup grid onto which regridding takes place
    outGrd = xr.Dataset(
    {
        "lat": (["lat"], np.arange(config['domain']['ymin'],
                                   config['domain']['ymax'],
                                   config['domain']['dy']),
                {"units": "degrees_north"}),
        "lon": (["lon"], np.arange(config['domain']['xmin'],
                                   config['domain']['xmax'],
                                   config['domain']['dx']),
                {"units": "degrees_east"})
    })
    
    #Setup xarray object
    dsIn= xr.open_dataset(inFile[0])
    
    #Do the regridding
    regridder = xe.Regridder(dsIn, outGrd, 
                             config['regridding']['method'],
                             unmapped_to_nan=True)
    dsout=regridder(dsIn)
    
    #Write out
    dname=os.path.dirname(outFile[0])
    if not os.path.exists(dname):
        os.makedirs(dname)
    dsout.to_netcdf(outFile[0])


    
    

