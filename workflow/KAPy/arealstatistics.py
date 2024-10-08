"""
#Setup for debugging with VS code 
import os
print(os.getcwd())
os.chdir("..")
import KAPy
os.chdir("..")
config=KAPy.getConfig("./config/config.yaml")  
wf=KAPy.getWorkflow(config)
ensID=next(iter(wf['ensstats'].keys()))
inFile=wf['ensstats'][ensID]
#Enable inline plotting in vscode
%matplotlib inline
"""

import xarray as xr
import pandas as pd
import geopandas as gpd
import regionmask
import numpy as np
import os

def generateArealstats(config, inFile, outFile):
    # Generate statistics over an area by applying a polygon mask and averaging
    # Setup xarray
    thisDat = xr.open_dataset(inFile[0]).indicator

    # If we have a shapefile defined, then work with it
    if config['arealstats']['shapefile']!='':
        #Import shapefile
        shapefile = gpd.GeoDataFrame.from_file(config['arealstats']['shapefile'])

        #Setup mask
        maskRegions=regionmask.from_geopandas(shapefile,
                                       names=config['arealstats']['idColumn'],
                                       abbrevs=config['arealstats']['idColumn'],
                                       name='test')
        maskRaster=maskRegions.mask_3D_frac_approx(thisDat)

        #Apply masking and calculate
        statDims=[d for d in thisDat.dims if d not in ['region','periodID','time','percentiles']]
        wtMean = thisDat.weighted(maskRaster).mean(dim=statDims)
        wtMean.name='mean'
        wtSd = thisDat.weighted(maskRaster).std(dim=statDims)
        wtSd.name='sd'
        wtUpper = thisDat.weighted(maskRaster).quantile(q=config['ensembles']['upperPercentile']/100,dim=statDims)
        wtUpper.name='upperPercentile'
        wtUpper = wtUpper.drop_vars('quantile')
        wtCentral = thisDat.weighted(maskRaster).quantile(q=config['ensembles']['centralPercentile']/100,dim=statDims)
        wtCentral.name='centralPercentile'
        wtCentral = wtCentral.drop_vars('quantile')        
        wtLower = thisDat.weighted(maskRaster).quantile(q=config['ensembles']['lowerPercentile']/100,dim=statDims)
        wtLower.name='lowerPercentile'
        wtLower = wtLower.drop_vars('quantile')

        #Output object
        dfOut=xr.merge([wtMean,wtSd,wtLower,wtCentral,wtUpper]).to_dataframe()
        dfOut=dfOut.rename(columns={'names':'area'})
        dfOut=dfOut.drop(columns=['abbrevs'])
        

    #Otherwise, just average spatially
    else:
        # Average spatially over the time dimension
        spDims =[d for d in thisDat.dims if d not in ['time','periodID','percentiles']]
        spMean = thisDat.mean(dim=spDims)
        spMean.name='mean'
        spSd = thisDat.mean(dim=spDims)
        spSd.name='sd'

        # Save files pandas
        dfOut = xr.merge([spMean,spSd]).to_dataframe()
        dfOut["area"] = "All"  
    
    #Write results out
    dfOut.to_csv(outFile[0])



"""
inFiles=wf['arealstats'].keys()
outFile=["results/5.areal_statistics/Areal_statistics.csv"]
"""

def combineArealstats(config, inFiles, outFile):
    #Load individual files
    dat = []
    for f in inFiles:
        datIn=pd.read_csv(f)
        datIn.insert(0,'sourcePath',f)
        datIn.insert(0,'filename',os.path.basename(f))
        dat += [datIn]
    datdf = pd.concat(dat)
    
    #Split out the defined elements
    datdf.insert(2,'memberID',datdf['filename'].str.extract("^[^_]+_[^_]+_[^_]+_[^_]+_(.*?).csv$"))
    datdf.insert(2,'expt',datdf['filename'].str.extract("^[^_]+_[^_]+_[^_]+_([^_]+)_.*$"))
    datdf.insert(2,'gridID',datdf['filename'].str.extract("^[^_]+_[^_]+_([^_]+)_.*$"))
    datdf.insert(2,'srcID',datdf['filename'].str.extract("^[^_]+_([^_]+)_.*$"))
    datdf.insert(2,'indID',datdf['filename'].str.extract("^([^_]+)_.*$"))

    #Drop the filename and write out
    datdf.drop(columns=['filename']).to_csv(outFile[0])

