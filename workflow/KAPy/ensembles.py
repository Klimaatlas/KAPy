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
#inFile=["./KAGh/6.ensstats/i101_ensstat_rcp85.nc"]

config_path= "../../config/config.yaml"
def regrid(config,inFile,outFile):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    #print("Config:", config) 

    outGrd = xr.Dataset(
    {
        "lat": (["lat"], np.arange(config['domain']['ymin'],
                                   config['domain']['ymax'],
                                   config['regridding']['dy']),
                {"units": "degrees_north"}),
        "lon": (["lon"], np.arange(config['domain']['xmin'],
                                   config['domain']['xmax'],
                                   config['regridding']['dx']),
                {"units": "degrees_east"})
    })

    if not inFile:
        raise ValueError("Empty list of inFile")
        

    #Setup xarray object
    dsIn= xr.open_dataset(inFile)

    regridder = xe.Regridder(dsIn, outGrd, 
                             method=config['regridding']['method'],
                             extrap_method=config['regridding']['extrap_method'])

    dsout=regridder(dsIn)
    
    #Write out
    dname=os.path.dirname(outFile)
    if not os.path.exists(dname):
        os.makedirs(dname)
    dsout.to_netcdf(outFile)
    

def generateEnsstats(config,infiles,outfile):
    #Setup the ensemble
    #Enforce a join='override' to handle differences between grids close to
    #numerical precision
    thisEns = xcEns.create_ensemble(infiles,multifile=True,join='override')  
    #Calculate the statistics
    ens_mean_std = xcEns.ensemble_mean_std_max_min(thisEns)
    ens_percs = xcEns.ensemble_percentiles(thisEns, split=False, 
                                           values=[x for x in config['ensembles'].values()])
    ensOut=xr.merge([ens_mean_std,ens_percs])
    #Write results
    ensOut.to_netcdf(outfile[0])

    
def generateArealstats(config,inFile,outFile):
    #Generate statistics over an area by applying a polygon mask and averaging
    #Setup xarray
    thisDat = xr.open_dataset(inFile[0])
    
    #Perform masking
    #TODO
    
    #Average spatially
    spMean=thisDat.indicator.mean(dim=["rlon","rlat"])
    
    #Save files pandas
    dfOut=spMean.to_dataframe()
    dfOut['area']='All'          # Currently place holder. Implement masking in future.
    dfOut.to_csv(outFile[0])

