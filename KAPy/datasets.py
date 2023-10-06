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
#allInputs=glob.glob(os.path.join(KAPy.getFullPath(config,'inputs'),"*.nc"))

def inferDatasets(config,allInputs):
    '''
    Make list of datasaet objects
    
    Given a directory of model inputs, this function infers the full list of xarray dataset 
    objects that should be formed as the basis for further processing. The grouping of 
    experiments is defined a priori in the 'scenarios' key in the configuration file - remember
    that we consider a 'dataset' as a grouping of one or more experiments into a coherent 
    time series.
    '''
    #Setup directories and list of scenarios to be considered
    flist=pd.DataFrame(allInputs,columns=['path'])
    flist['fname']=[os.path.basename(p) for p in flist.path]
    exptList=np.unique([cfg['experiments'] for cfg in config['scenarios'].values()]).tolist()
    
    #Split file list into chunks
    pat=f'(.+)_({"|".join(exptList)})_(.+)_([^_]+).nc'
    flist[['prefix', 'expt', 'suffix','date']] = flist['fname'].str.extract(pat)
    
    #Loop over scenarios to generate the filename
    xrList=[]
    for sc in config['scenarios'].values():
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
    #Find the scenario that the object is based on
    scList=[sc['shortname'] for sc in config['scenarios'].values()]
    grpPat=f'(?P<Prefix>.+)_(?P<Scen>[{"|".join(scList)}]+)_(?P<Suffix>.+).nc.pkl'
    grps=re.match(grpPat,thisDs)
    thisSc=[sc for sc in config['scenarios'].values() if sc['shortname']==grps.group('Scen')]
    
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
    
    #Write the dataset object to disk, as a pickle
    with open(outFile[0],'wb') as f:
        pickle.dump(ds,f,protocol=-1)
    


def makeDatasets(config):
    '''
    Make xarray datasets
    to get the same effect as above. Note that in contrast to the input directive, the params directive can optionally take more arguments than only wildcards, namely input, output, threads, and resources. From the Python perspective, they can be seen as optional keyword arguments without a default value. Their order does not matter, apart from the fact that wildcards has to be the first argument. In the example above, this allows you to derive the prefix name from the output file.
    Merges together files into a coherent timeseries along their time dimension.
    The merging is done by creating an xarray dataset, that is then written to disk
    in a "pickled" format, from where it can be reloaded later.
    
    File paths are deduced from the configuration file
    '''
    #Setup directories and filelist
    srcPath=KAPy.getFullPath(config,'modelInputs')
    flist=pd.DataFrame(os.listdir(srcPath),columns=['fname'])

    #Split into variable types and apply naming accordingly
    #ASSERT: Data follows CORDEX naming convention
    #See document here for details
    #https://is-enes-data.github.io/cordex_archive_specifications.pdf
    colNames=['VariableName', 'Domain', 'GCMModelName', 'CMIP5ExperimentName', 'CMIP5EnsembleMember','RCMModelName', 'RCMVersionID', 'Frequency', 'Other']
    flistMeta=flist.fname.str.split('_',expand=True,n=8)
    flistMeta.columns=colNames
    flist=pd.concat([flist,flistMeta],axis=1)
    flist['path']=srcPath+os.sep+flist.fname

    #Setup for output
    xrPath=KAPy.getFullPath(config,'xarrays')
    if not os.path.exists(xrPath):
        os.makedirs(xrPath)
   
    #Now we build the xarray datasets. First we groupby everything except 
    #the leftovers and the CMIP5ExperimentName
    grpNames=[x for x in colNames if x not in [ 'CMIP5ExperimentName','Other']]
    for name,df in tqdm.tqdm(flist.groupby(grpNames)):
        #Lets get the list of experiments that we have in this group
        exptsPresent=list(df.CMIP5ExperimentName.unique())
        #Extract out historical
        histFlist=df[df['CMIP5ExperimentName']=="historical"]
        #Loop over scenarios
        for sc in [x for x in exptsPresent if x!='historical']:
            #Extract this scenario from the filelist
            scFlist=df[df['CMIP5ExperimentName']==sc]
            #Make dataset object, sorted on time
            outFlist=pd.concat([histFlist,scFlist])
            ds =xr.open_mfdataset(outFlist.path,
                             combine='nested',
                            concat_dim='time')
            ds=ds.sortby('time')
            #Setup output filename - need to put the expt back in the right place
            dsName='_'.join(name[:3]+(sc,)+name[3:])+'.pkl'
            #Write the xarray dataset object to disk, as a pickle
            with open(os.path.join(xrPath,dsName),'wb') as f:
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
