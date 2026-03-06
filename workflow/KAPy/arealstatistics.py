import xarray as xr
import pandas as pd
import geopandas as gpd
from cdo import Cdo
import regionmask
import numpy as np

"""
#Setup for debugging with VS code 
import os
print(os.getcwd())
os.chdir("..")
import workflow.KAPy as KAPy
config=KAPy.getConfig("./workflow/testing/config.yaml") 
config=KAPy.getConfig("./config/config.yaml") 
wf=KAPy.getWorkflow(config)
asID=list(wf['arealstats']['input_dict'].keys())[0]
inFile=wf['arealstats']['input_dict'][asID]
shapefile=config["arealstats"]['shapefile']
useAreaWeighting=config["arealstats"]['useAreaWeighting']
tempDir=config['dirs']['tempDir']
%matplotlib inline
"""

def generateArealstats(outFile, inFile, tempDir,useAreaWeighting,shapefile):
    # Generate statistics over an area by applying a polygon mask and averaging
    # Setup xarray
    # Note that we need to use open_dataset here, as the ensemble files have
    # multiple data variables in them
    time_coder=xr.coders.CFDatetimeCoder(use_cftime=True)
    thisDat = xr.open_dataset(inFile[0],
                              decode_times=time_coder)

    #Identify the time / period coordinate first
    if 'time' in thisDat.dims:
        tCoord='time'
    elif 'periodID' in thisDat.dims:
        tCoord='periodID'
    else:
        raise ValueError(f'Cannot find time or periodID coordinate in "{inFile[0]}".')
    
    #Identify coordinate types. Some logic is required here, as the coordinates
    #presented can vary based on time_binning and whether it is an ensemble stat or member
    spDims =list(set(thisDat.dims)-set(['time','periodID',"seasonID",'percentiles']))
    nonspDims=list(set(thisDat.dims)-set(spDims))
    spGrid=thisDat.isel({k : 0 for k in nonspDims},drop=True)[list(thisDat.data_vars)[0]]

    # If using area weighting, get the pixel size
    if useAreaWeighting:
        cdo=Cdo(tempdir=tempDir)
        pxlSize=cdo.gridarea(input=spGrid,returnXArray='cell_area')
    else:
        pxlSize=spGrid
        pxlSize.values[:]=1
        pxlSize.name="cell_area"

    # If we have a shapefile defined, then work with it
    if shapefile is not None:
        #Import shapefile
        shpFile = gpd.read_file(shapefile)

        #If the shapefile is missing a CRS, stop - we don't want to assume anything here
        if shpFile.crs is None:
            raise ImportError(f"Shapefile '{shapefile}' is lacking a CRS (Coordinate Reference System) "+
                              "but this is required for KAPy to work. Please add a CRS in the shapefile.")
        
        #Handle projection issues. 
        # 1. If the file has supplementary coordinates of longitude and latitude, then reproject
        #    the shapefile to long-lat and use together with the supplementary coordinates
        if bool(set(['lat','latitude']) & set(thisDat.coords)) & bool(set(['lon','longitude']) & set(thisDat.coords)):
            shpFile = shpFile.to_crs("EPSG:4326")  #Lon-lat
            xDim= spGrid[ 'lon' if 'lon' in list(spGrid.coords) else 'longitude']
            yDim= spGrid[ 'lat' if 'lat' in list(spGrid.coords) else 'latitude']
            useSupCoords=True

        # 2. Otherwise assert that the user has checked that the two CRS match.
        #    Ideally we should check this, but I'm not convinced that it can be done robustly.
        else:
            useSupCoords=False

        #Loop over polygons
        outList=[]
        for thisIdx, thisArea in shpFile.iterrows():
            #Which points are in the polygon? Setup a mask
            if useSupCoords:
                pxlMask=regionmask.mask_geopandas(shpFile.iloc[[thisIdx]],xDim,yDim)
            else:
                pxlMask=regionmask.mask_geopandas(shpFile.iloc[[thisIdx]],spGrid)
            pxlWts = xr.where(~pxlMask.isnull(), pxlSize, 0)
            
            #Apply masking and weighting and calculate
            wtMeanDf = thisDat.weighted(pxlWts).mean(dim=spDims).to_dataframe().reset_index()
            wtMeanDf['arealStatistic']='mean'
            wtSdDf = thisDat.weighted(pxlWts).std(dim=spDims).to_dataframe().reset_index()
            wtSdDf['arealStatistic']='sd'

            #Output object
            thisOut=pd.concat([wtMeanDf,wtSdDf])
            thisOut.insert(0,'areaID',thisIdx )
            outList += [thisOut]
        dfOut=pd.concat(outList)

    #Otherwise, just average spatially
    else:
        # Average spatially over the time dimension
        spMean = thisDat.weighted(pxlSize).mean(dim=spDims)
        spMeanDf=spMean.to_dataframe()
        spMeanDf['arealStatistic']='mean'
        spSd = thisDat.weighted(pxlSize).std(dim=spDims)
        spSdDf=spSd.to_dataframe()
        spSdDf['arealStatistic']='sd'

        # Save files pandas
        dfOut = pd.concat([spMeanDf,spSdDf])
        dfOut.insert(0,'areaID',"all" )
        dfOut=dfOut.reset_index()

    #Write out date without time for easier handling
    if 'time' in dfOut.columns:
        dfOut['time']=[d.strftime("%Y-%m-%d") for d in dfOut['time']]
    
    #Write results out
    dfOut.to_csv(outFile[0],index=False)



