import sqlite3
import pandas as pd
import os
import xarray as xr

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
        datIn=pd.read_csv(thisPath)
        
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

"""
ensstats=wf['database']['ensstats']
members=wf['database']['members']
outFile=[os.path.join(config['dirs']['outputs'],'KAPy_outputs.sqlite')]
"""


def writeToDatabase(outFile, ensstats, members):
    # Connect to (or create) a SQLite database - Delete the file if it exists
    if os.path.exists(outFile[0]):
        os.remove(outFile[0])
    conn = sqlite3.connect(outFile[0])

    # Create ensemble members table
    conn.execute("""
        CREATE TABLE Ensemble_members (
            datasetID TEXT NOT NULL,
            indID TEXT NOT NULL,
            gridID TEXT NOT NULL,
            expt TEXT NOT NULL,
            memberID TEXT NOT NULL,
            areaID TEXT NOT NULL,
            seasonID TEXT NOT NULL,
            periodID TEXT NOT NULL,
            arealStatistic TEXT NOT NULL,
            indicator REAL,
            delta REAL
        );
        """)

    #Load and then write member statistics
    with conn:  # wraps everything in one transaction
        for df in pd.read_csv(members[0], chunksize=100_000):
            df.to_sql("Ensemble_members", conn, if_exists="append", index=False)

    # Create ensemble statistics table
    conn.execute("""
        CREATE TABLE Ensemble_statistics (
            datasetID TEXT NOT NULL,
            indID TEXT NOT NULL,
            gridID TEXT NOT NULL,
            expt TEXT NOT NULL,
            memberID TEXT NOT NULL,
            areaID TEXT NOT NULL,
            seasonID TEXT NOT NULL,
            periodID TEXT NOT NULL,
            percentiles REAL,
            arealStatistic TEXT NOT NULL,
            indicator_mean REAL,
            indicator_n INTEGER,
            indicator_max REAL,
            indicator_min REAL,
            indicator_percentiles REAL,
            indicator_stdev REAL,
            delta_mean REAL,
            delta_n INTEGER,
            delta_max REAL,
            delta_min REAL,
            delta_percentiles REAL,
            delta_stdev REAL
        );
    """)

    #Load and then write ensemble statistics
    with conn:  # wraps everything in one transaction
        for df in pd.read_csv(ensstats[0], chunksize=100_000):
            df.to_sql("Ensemble_statistics", conn, if_exists="append", index=False)

    #Set indexing
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX idx_ensstats ON Ensemble_statistics(datasetID,indID,gridID,expt,seasonID,periodID,percentiles,areaID)")
    cursor.execute("CREATE INDEX idx_members ON Ensemble_members(datasetID,indID,gridID,expt, areaID,seasonID,periodID)")

    # Commit and close
    conn.commit()
    conn.close()


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

    def write_dataarray(da: xr.DataArray,var_name: str, 
                        output_path: str):
            da.name = var_name
            chunkThisWay=[min([256,16,16][i],da.shape[i]) for i in range(0,3)]
            da.to_netcdf(output_path,
                        encoding={var_name:{'chunksizes':chunkThisWay,
                                        'zlib': True,
                                        'complevel':1}})

    if isinstance(obj, xr.DataArray):
        # Expect exactly one key in path
        if len(path) != 1:
            raise ValueError("Expected exactly one path for a single DataArray")
        write_dataarray(obj,
                        var_name=next(iter(path.keys())),
                        output_path = next(iter(path.values())))
    
    elif isinstance(obj, xr.Dataset):
        for var in path.keys():
            if var not in obj:
                raise KeyError(f"Cannot find variable '{var}' in provided dataset")
            dat=obj[var]
            write_dataarray(dat,
                            var_name=var,
                            output_path = path[var])
        
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
        print(path)
        obj.to_netcdf(path[0])
    
    elif isinstance(obj, dict):
        for ind in path.keys():
            if ind not in obj:
                raise KeyError(f"Cannot find indicator '{ind}' in provided dict to write with keys {obj.keys()}")
            dat=obj[ind]
            dat.to_netcdf( path[ind])
        
    else:
        raise TypeError(f"Unsupported type: {type(obj)}")







