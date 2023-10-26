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
#allInputs=glob.glob(KAPy.buildPath(config,'inputs',"*.nc"))

def inferDatasets(config,allInputs):
    '''
    Make list of datasaet objects
    
    Given a directory of model inputs, this function infers the full list of xarray dataset 
    objects that should be formed as the basis for further processing. The grouping of 
    experiments is defined a priori in the 'datasets' key in the configuration file - remember
    that we consider a 'dataset' as a grouping of one or more experiments into a coherent 
    time series.
    '''
    #Setup directories and list of datasets to be considered
    flist=pd.DataFrame(allInputs,columns=['path'])
    flist['fname']=[os.path.basename(p) for p in flist.path]
    exptList=np.unique([cfg['experiments'] for cfg in config['datasets'].values()]).tolist()
    
    #Split file list into chunks
    pat=f'(.+)_({"|".join(exptList)})_(.+)_([^_]+).nc'
    flist[['prefix', 'expt', 'suffix','date']] = flist['fname'].str.extract(pat)
    
    #Loop over dataset definitions to generate the filename
    xrList=[]
    for sc in config['datasets'].values():
        theseFiles=flist[flist.expt.isin(sc['experiments'])].copy()
        theseFiles['xarrayFname'] = theseFiles.prefix + "_" + \
                                    sc['shortname'] + "_" + theseFiles.suffix + ".nc.pkl"
        xrList += theseFiles.xarrayFname.tolist()
    
    #Tidy up, removing the duplicates
    rtn=np.unique(xrList).tolist()
    return(rtn)

def deduceDatasetInputs(config,thisDs,allInputs):
    """
    Find the input files for a given dataset object
    
    Give a path to a proposed dataset object, this function finds all of the available 
    model inputs that should be used to build it
    """
    #Find the dataset that the object is based on
    scList=[sc['shortname'] for sc in config['datasets'].values()]
    grpPat=f'(?P<Prefix>.+)_(?P<DataSet>[{"|".join(scList)}]+)_(?P<Suffix>.+).nc.pkl'
    grps=re.match(grpPat,thisDs)
    thisSc=[sc for sc in config['datasets'].values() if sc['shortname']==grps.group('DataSet')]
    
    #Now filter the file list using regex. Need to supply the list as an argument
    inPat  =f"{grps.group('Prefix')}_"+\
            f"({'|'.join(thisSc[0]['experiments'])})_" +\
            f"{grps.group('Suffix')}_.+.nc"
    inFiles = [file for file in allInputs if re.match(inPat, os.path.basename(file))]
    return(inFiles)
 
def buildDataset(config,inFiles,outFile):
    """
    Build the data object
    
    Build the set of input files into a single xarray-based dataset object
    and pickle it
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

    #Write the dataset object to disk, as a pickle
    with open(outFile[0],'wb') as f:
        pickle.dump(ds,f,protocol=-1)

"""
#retrieveVariables function
#Arguments
#makeDatasets(datPath='/dmidata/projects/klimaatlas/pipeline/outputs/netcdf/BC/v2023a/',
#            pklPath='./scratch/v2023a/')
pklPath=os.path.join('scratch','v2023a')
VariableName=['tas','pr']
Frequency=['day']

#Setup alist of files
flist=pd.DataFrame(os.listdir(pklPath),columns=['fname'])

#Split into variable types and apply naming accordingly
#ASSERT: Data follows CORDEX naming convention
#See document here for details
#https://is-enes-data.github.io/cordex_archive_specifications.pdf
colNames=['VariableName', 'Domain', 'GCMModelName', 'CMIP5ExperimentName', 'CMIP5EnsembleMember','RCMModelName', 'RCMVersionID', 'Frequency']
flistMeta=flist.fname.str.removesuffix('.pkl').str.split('_',expand=True)
flistMeta.columns=colNames
flist=pd.concat([flist,flistMeta],axis=1)
flist['path']=pklPath+os.sep+flist.fname

#Now filter to retain variables of interest
selList=flist
selList=selList[selList['VariableName'].isin(VariableName)]
selList=selList[selList['Frequency'].isin(Frequency)]

#Load the dataset objects into the dataframe
selList.apply()
l=selList.groupby(colNames[1:])

#TODO:
# * Load the dataset objects into the dataframe
# * Groupby, and then lump them together
# * Return as a list (??) or dataframe that can be used elsewhere. May need some metadata here to accompany them.

"""
