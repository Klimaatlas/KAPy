import pandas as pd
import os
import xarray as xr
import pickle
from pathlib import Path
import shutil

"""
#Setup for debugging with VS code 
import os
print(os.getcwd())
os.chdir("..")
import KAPy
os.chdir("../..")
config=KAPy.getConfig("./config/config.yaml")  
wf=KAPy.getWorkflow(config)
%matplotlib inline
inFiles=wf['mergedCSVs']['members']
"""

def mergeCSVs(outFile, inFiles):
    #Load data file function
    def prepareDataFile(thisPath):
        #Load file
        datIn=pd.read_csv(thisPath,dtype=str,keep_default_na=False)
        
        #Process filename 
        datIn.insert(0,'filename',os.path.basename(thisPath))
        datIn.insert(2,'memberID',datIn['filename'].str.extract("^[^_]+_[^_]+_[^_]+_[^_]+_(.*).csv$"))
        datIn.insert(2,'expt',datIn['filename'].str.extract("^[^_]+_[^_]+_[^_]+_([^_]+)_.*$"))
        datIn.insert(2,'gridID',datIn['filename'].str.extract("^[^_]+_[^_]+_([^_]+)_.*$"))
        datIn.insert(2,'datasetID',datIn['filename'].str.extract("^([^_]+)_.*$"))
        datIn.insert(2,'indID',datIn['filename'].str.extract("^[^_]+_([^_]+)_.*$"))

        #Finish
        datOut=datIn.drop(columns=["filename"])
        return(datOut)
    
    # Delete the output file if it exists
    if os.path.exists(outFile[0]):
        os.remove(outFile[0])
    
    #Load and then write data individually to a merged file
    #Only write the header if the file doesn't exist
    hasHeader=False
    for f in inFiles:
        df = prepareDataFile(f)
        df.to_csv(outFile[0],index=False,mode="a",header=not hasHeader)
        hasHeader=True


def write_variables(obj: xr.DataArray | xr.Dataset | dict, 
                  path: dict[str, str]) -> None:
    """
    Write variables as xarray objects to disk as NetCDF files.

    Parameters
    ----------
    obj : xr.DataArray, xr.Dataset
        The data to write. If a Dataset multiple files are written.
    path : dict
        Mapping of variable names to output file paths.
        For a single DataArray, should have one key matching the variable name.
        For a Dataset, keys should match dataset variables.
    """

    def write_dataarray(da: xr.DataArray,
                        var_name: str, 
                        output_path: str):
            #Choose output format
            format = os.path.splitext(os.path.basename(output_path))[1]
            if format == ".nc":
                da.name = var_name
                chunkThisWay=[min([256,16,16][i],da.shape[i]) for i in range(0,3)]
                da.to_netcdf(output_path,
                            encoding={var_name:{'chunksizes':chunkThisWay,
                                            'zlib': True,
                                            'complevel':1}})
            elif format == ".pkl":  # Write as pickle
                with open(output_path, "wb") as f:
                    pickle.dump(da, f)                    
            else:
                raise IOError(f"Unknown file format, '{format}' inferred from: '{output_path}'.")

    if isinstance(obj, xr.DataArray):
        # Expect exactly one key in path
        if len(path) != 1:
            raise ValueError(f"Expected exactly one path for a single DataArray: received {path}")
        write_dataarray(obj,
                        var_name=next(iter(path.keys())),
                        output_path = next(iter(path.values())))
    
    elif isinstance(obj,dict):
        #Accept instances where the object is a dict of paths to a file.
        #There should be agreement between the keys in the path and obj file.
        #Check this first
        if not obj.keys()== path.keys():
            raise ValueError(f"Mismatch between variables expected and returned by the function. Expected: {list(path.keys())}. Returned: {list(obj.keys())}")
        #Loop over the dicts. If the path contained in the object matches the desired output path,
        #then the result should already be in the right place. Else move the file in  obj to the output path
        for this_key in obj.keys():
            if obj[this_key]!=path[this_key]:
                shutil.move(Path(obj[this_key]),Path(path[this_key]))
        
    else:
        raise TypeError(f"Unsupported type: {type(obj)}")



def write_indicators(obj:  xr.Dataset | dict, 
                  path: dict[str, str]) -> None:
    """
    Write indicators to disk as NetCDF files.

    Parameters
    ----------
    obj :  xr.Dataset | dict
        The data to write, provided either as a dataset or a dict. If a dict multiple files are written.
    path : dict
        Mapping of indicator names to output file paths.
    """

    if isinstance(obj, xr.Dataset):
        # Expect exactly one key in path
        if len(path) != 1:
            raise ValueError("Expected exactly one path for a single dataset")
        if isinstance(path,dict):
            path=list(path.values())
        obj.to_netcdf(path[0])
    
    elif isinstance(obj, dict):
        for ind in path.keys():
            if ind not in obj:
                raise KeyError(f"Cannot find indicator '{ind}' in provided dict to write with keys {obj.keys()}")
            dat=obj[ind]
            dat.to_netcdf( path[ind])
        
    else:
        raise TypeError(f"Unsupported type: {type(obj)}")







