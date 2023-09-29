import KAPy
import pandas as pd
import os
import xarray as xr
import xclim.ensembles as xcEns
import xesmf as xe
import pickle
import numpy as np
import tqdm

def makeDatasets(srcPath,xrPath,cfg):
    '''
    Make xarray datasets
    
    Merges together files that are otherwise from the same experiment along
    their time dimension. The merging is done by creating an xarray dataset, that 
    is then written to disk in a "pickled" format, from where it can be reloaded
    later.
    '''
    #Setup alist of files
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

    #Now we groupby everything except the last column name (the leftovers)
    #We loop over each group, building an xarray dataset and writing 
    #the object to disk
    for name,df in tqdm.tqdm(flist.groupby(colNames[:-1])):
        #Setup output filename
        dsName='_'.join(name)+'.pkl'
        #Make dataset object, sorted on the last set of values first
        df=df.sort_values(colNames[:-1])
        ds =xr.open_mfdataset(df.path,
                             combine='nested',
                            concat_dim='time')
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

def generateEnsstats(infiles,outfile,config):
    #Setup the ensemble
    #Enforce a join='override' to handle differences between grids close to
    #numerical precision
    thisEns = xcEns.create_ensemble(infiles,multifile=True,join='override')  
    #Calculate the statistics
    ens_mean_std = xcEns.ensemble_mean_std_max_min(thisEns)
    ens_percs = xcEns.ensemble_percentiles(thisEns, values=config['percentiles'])
    ensOut=xr.merge([ens_mean_std,ens_percs])
    #Write results
    ensOut.to_netcdf(outfile[0])
    
    
    
def regrid(inFile,outFile,config):
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
                             config['domain']['method'],
                             unmapped_to_nan=True)
    dsout=regridder(dsIn)
    
    #Write out
    dsout.to_netcdf(outFile[0])


    
    

