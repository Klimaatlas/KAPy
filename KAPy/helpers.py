"""
import os
print(os.getcwd())
os.chdir("..")
os.chdir("..")
thisPath='outputs/1.variables/tas/tas_CORDEX_EUR-11_rcp85_IPSL-IPSL-CM5A-MR_r1i1p1_DMI-HIRHAM5_v1.nc'
"""

import pickle
import xarray as xr
import os
import importlib


def readFile(thisPath,format=None,chunks={}):
    """
    Read a file from given path.

    The file can be stored as either a pickle (.pkl) or a NetCDF (.nc) file. NetCDF files
    can be loaded directly into RAM, or referenced via dask

    Parameters
    ----------
    thisPath : _type_
        Path to the file
    format : _type_, optional
        In cases where the format of the file cannot be inferred from the extension, use 
        this argument to tell which format to use.
    chunks: _type_ dict
        Chunks argument to be supplied when opening file(s). The default, "{}", tells
        xarray to use the built-in chunking.

    Returns
    -------
    _type_
        XArray object

    Raises
    ------
    ValueError
        _description_
    IOError
        _description_
    """
    # Reads a dataset from disk, determining dynmaically whether it is
    # pickled or NetCDF based on the file extension
    if format==None:
        format = os.path.splitext(os.path.basename(thisPath))[1]
    if format == ".nc":
        try:
            time_coder=xr.coders.CFDatetimeCoder(use_cftime=True)
            thisDat = xr.open_dataarray(thisPath,
                                        chunks=chunks, #Use supplied chunking
                                        decode_times=time_coder)
        except Exception as e:
            raise IOError(f"Failed to open NetCDF file '{thisPath}': {e}")
    
        #Each file should only contain one variable, but we also need
        #to handle the situation where there is CRS information stored
        #as a variable. Hence, we open as a dataset, and then proceed
        #from there
        # if useDask:
        #     thisDS = xr.open_mfdataset(thisPath,
        #                                 use_cftime=True)
        # else:
        #     thisDS = xr.open_dataset(thisPath,
        #                                 use_cftime=True)
        # #Check for more than one non-CRS value
        # if ('crs' in thisDS.data_vars) & (len(list(thisDS.data_vars))==2):
        #     thisVar=[k for k in thisDS.data_vars if k != "crs"]
        #     thisDat=thisDS[thisVar[0]]
        # elif (len(list(thisDS.data_vars))==1):
        #     thisDat=thisDS[list(thisDS.data_vars)[0]]
        # else:
        #     raise ValueError(f"{thisPath} contains more than one (non-CRS) variable. " +
        #                f"The variables are {list(thisDS.data_vars)}")
    elif format == ".pkl":  # Read pickle
        with open(thisPath, "rb") as f:
            thisDat = pickle.load(f)
    else:
        raise IOError(f"Unknown file format, '{format}' inferred from: '{thisPath}'.")
    return thisDat


def timeslice(this,startYr,endYr):
    # Slice dataset
    timemin = this.time.dt.year >= int(startYr)
    timemax = this.time.dt.year <= int(endYr)
    sliced = this.sel(time=timemin & timemax)
    return sliced


def getExternalFunction(scriptPath,functionName):
    """
    Retrieves a function from an external file 

    Args:
        scriptPath (_type_): Path to the script file containing the function
        functionName (_type_): Name of the function to retrieve
    """
    thisSpec = importlib.util.spec_from_file_location("customScript", scriptPath)
    thisModule = importlib.util.module_from_spec(thisSpec)
    thisSpec.loader.exec_module(thisModule)
    thisFn = getattr(thisModule, functionName)
    return(thisFn)
