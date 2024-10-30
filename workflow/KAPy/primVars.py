"""
#Setup for debugging with VSCode
import os
print(os.getcwd())
os.chdir("..")
import KAPy
os.chdir("..")
os.chdir("..")
print(os.getcwd())
config=KAPy.getConfig("./config/config.yaml")  
wf=KAPy.getWorkflow(config)
inpID=next(iter(wf['primVars'].keys()))
outFile=[next(iter(wf['primVars'][inpID]))]
inFiles=wf['primVars'][inpID][outFile[0]]
%matplotlib qt
import matplotlib.pyplot as plt
"""

# Given a set of input files, create objects that can be worked with
import xarray as xr
import pickle
import sys
import importlib
from cdo import Cdo
import geopandas as gpd

def buildPrimVar(config, inFiles, outFile, inpID):
    """
    Build the data object

    Build the set of input files into a single xarray-based dataset object
    and write it out, either as a NetCDF file or as a pickle.
    """
    # Get input configuration
    thisInp = config["inputs"][inpID]

    # Make dataset object using xarray lazy load approach.
    # Apply a manual sort ensures that the time axis is correct
    # Use the join="override" argument to handle the case where
    # there are small numerical differences in the values of the
    # coordinates - in this case, we take the coordinates from the first file
    dsIn =xr.open_mfdataset(inFiles,
                            combine='nested',
                            use_cftime=True, 
                            join="override", 
                            concat_dim='time')
    dsIn=dsIn.sortby('time')

    # Select the desired variable and rename it
    ds = dsIn.rename({thisInp["internalVarName"]: thisInp["varID"]})
    da = ds[thisInp["varID"]]  # Convert to dataarray

    # Drop degenerate dimensions. If any remain, throw an error
    da = da.squeeze(drop=True)
    if len(da.dims) != 3:
        sys.exit(
            f"Extra dimensions found in processing '{inpID}' - there should be only "
            + f"three dimensions after degenerate dimensions are dropped but "
            + f"found {len(da.dims)} i.e. {da.dims}."
        )

    # Drop coordinates that are not associated with a dimension. Often you seen
    # height or level coming in as a coordinate, when it is perhaps more appropriate as
    # an attribute. However, different models handle this differently, and some have
    # already dropped it. The different between the two can cause problems when we
    # come to the point of merging ensemble members.
    for thisCoord in da.coords.keys():
        if len(da[thisCoord].dims)==0:
            da.attrs[thisCoord]=da[thisCoord].values
            da= da.drop_vars(thisCoord)

    #Apply cutout functionality
    if config["cutouts"]["method"] == "lonlatbox":
        # The processing chain here is to first take
        # a slide, and then do a cdo cutoout on it. This
        # can be used as a mask on the xarray object - this
        # way we can maintain the lazy-loading and storage benefits
        # associated with pickling
        
        # Extract first time step. This avoids having to work
        # with the entire dataset
        firstTS=da.isel(time=0)

        # Do cutouts using cdo sellonlatbox. Make sure that we
        # return a dataarray and not a dataset
        cdo = Cdo()
        cutoutMask = cdo.sellonlatbox(
            config["cutouts"]["xmin"],
            config["cutouts"]["xmax"],
            config["cutouts"]["ymin"],
            config["cutouts"]["ymax"],
            input=firstTS,
            returnXArray=thisInp["varID"])
        
        # Apply masking to data array object
        da=da.where(cutoutMask.notnull(),drop=True)

    elif config["cutouts"]["method"] != "shapefile":
  #  elif config["cutouts"]["method"] == "shapefile":
        #problem
  #      shapefile = gpd.GeoDataFrame.from_file(config['arealstats']['shapefile'])
  #      da.rio.set_spatial_dims(x_dim="rlon", y_dim="rlat", inplace=True)
  #      da.rio.write_crs("EPSG:4326", inplace=True)
  #      da = da.rio.clip(shapefile.geometry, shapefile.crs, drop=True)
        sys.exit(f"Unsupported cutout option '{config['cutouts']['method']}'.")

    # # Apply additional preprocessing scripts
    # if thisInp["importScriptPath"]!='':
    #     thisSpec = importlib.util.spec_from_file_location(
    #         "customScript", thisInp["importScriptPath"]
    #     )
    #     thisModule = importlib.util.module_from_spec(thisSpec)
    #     thisSpec.loader.exec_module(thisModule)
    #     ppFn = getattr(thisModule, thisInp["importScriptFunction"])
    #     da = ppFn(da)  # Assume no input arguments

    # Write the dataset object to disk, depending on the configuration
    if config['processing']['picklePrimaryVariables']:
        with open(outFile[0],'wb') as f:
            pickle.dump(da,f,protocol=-1)
    else:
        da.to_netcdf(outFile[0])
