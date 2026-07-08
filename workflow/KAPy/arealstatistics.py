import xarray as xr
import pandas as pd
import geopandas as gpd
from cdo import Cdo
import regionmask
import numpy as np

def generateArealstats(inFile, tempDir,useAreaWeighting,shapefile):
    """
    Generate statistics over an area by applying a polygon mask and averaging

    Parameters
    ----------
    inFile : _type_
        _description_
    tempDir : _type_
        _description_
    useAreaWeighting : _type_
        _description_
    shapefile : _type_
        _description_

    Returns
    -------
    _type_
        _description_

    Raises
    ------
    ValueError
        _description_
    ImportError
        _description_
    """

    # Setup xarray
    # Note that we need to use open_dataset here, as the ensemble files have
    # multiple data variables in them
    time_coder=xr.coders.CFDatetimeCoder(use_cftime=True)
    thisDat = xr.open_dataset(inFile,
                              decode_times=time_coder,
                              decode_timedelta=False)

    #Check for the presence  the time / period coordinate first
    if not any(coord in thisDat.dims for coord in ["time", "periodID"]):
        raise ValueError(f'Cannot find time or periodID coordinate in "{inFile}".')
    
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
        #Reset the index to be 0..N so that we avoid any potential auto-indexing from geopandas
        shpFile = gpd.read_file(shapefile)
        shpFile = shpFile.reset_index(drop=True)


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
            wtMeanDf['statisticType']='mean'
            wtSdDf = thisDat.weighted(pxlWts).std(dim=spDims).to_dataframe().reset_index()
            wtSdDf['statisticType']='sd'

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
        spMeanDf['statisticType']='mean'
        spSd = thisDat.weighted(pxlSize).std(dim=spDims)
        spSdDf=spSd.to_dataframe()
        spSdDf['statisticType']='sd'

        # Save files pandas. Set the areaID to NA
        dfOut = pd.concat([spMeanDf,spSdDf])
        dfOut.insert(0,'areaID',"NA" )
        dfOut=dfOut.reset_index()

    #Align different time axes into a "timebin" axis.
    if 'time' in dfOut.columns:
        dfOut['time']=[d.strftime("%Y-%m-%d") for d in dfOut['time']]
        dfOut=dfOut.rename(columns={"time": "timeBinID"})
    if 'periodID' in dfOut.columns:
        dfOut=dfOut.rename(columns={"periodID": "timeBinID"})

    #Return dfOut. Writing is handled by the calling function
    return dfOut


# Development setup -----------------------------------------------------
# Uses the testing dataset
if __name__ == "__main__":
    #Set the working directory 
    from pathlib import Path
    ROOT = Path(__file__).resolve().parent.parent.parent

    #Import KAPy
    os.chdir(ROOT/ "workflow")
    import KAPy
   
    #Setup configuration parameters
    import tempfile
    inFile= ROOT / "testing" / "07.ensstats" / "CORDEX-BA_i101_Ghana025_historical+rcp85_ensstats.nc"
    inFile= ROOT / "testing" / "07.ensstats" / "CORDEX-BA_T25_Ghana025_historical+rcp85_ensstats.nc"
    inFile= ROOT / "testing" / "07.ensstats" / "CORDEX-BA_mean-tas_Ghana025_historical+rcp85_ensstats.nc"
    tempDir=tempfile.gettempdir()
    useAreaWeighting=True
    shapefile= ROOT / 'docs/tutorials/Tutorial05_files/Ghana_regions.shp'
    
    #Run the function
    dfOut=generateArealstats(inFile,tempDir,useAreaWeighting,shapefile)
   

