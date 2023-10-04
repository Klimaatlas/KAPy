import KAPy
import pandas as pd
import os
import xarray as xr
import xclim.ensembles as xcEns
import xesmf as xe
import pickle
import numpy as np
import tqdm
import sys

#config=KAPy.loadConfig()  

def makeDatasets(config):
    '''
    Make xarray datasets
    
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

def generateEnsstats(config,infiles,outfile):
    #Setup the ensemble
    #Enforce a join='override' to handle differences between grids close to
    #numerical precision
    thisEns = xcEns.create_ensemble(infiles,multifile=True,join='override')  
    #Calculate the statistics
    ens_mean_std = xcEns.ensemble_mean_std_max_min(thisEns)
    ens_percs = xcEns.ensemble_percentiles(thisEns, values=config['ensembles']['percentiles'])
    ensOut=xr.merge([ens_mean_std,ens_percs])
    #Write results
    ensOut.to_netcdf(outfile[0])
    
    
    
def regrid(config,inFile,outFile,):
    #Setup grid onto which regridding takes place
    outGrd = xr.Dataset(
    {
        "lat": (["lat"], np.arange(config['domain']['ymin'],
                                   config['domain']['ymax'],
                                   config['domain']['dy']),
                {"units": "degrees_north"}),
        "lon": (["lon"], np.arange(config['domain']['xmin'],
                                   config['domain']['xmax'],
                                   config['domain']['dx']),
                {"units": "degrees_east"})
    })
    
    #Setup xarray object
    dsIn= xr.open_dataset(inFile[0])
    
    #Do the regridding
    regridder = xe.Regridder(dsIn, outGrd, 
                             config['regridding']['method'],
                             unmapped_to_nan=True)
    dsout=regridder(dsIn)
    
    #Write out
    dname=os.path.dirname(outFile[0])
    if not os.path.exists(dname):
        os.makedirs(dname)
    dsout.to_netcdf(outFile[0])


    
    

