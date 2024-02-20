#Given a set of input files, create datachunk objects that can be worked with

import KAPy
import pandas as pd
import os
import sys
import glob
import re

#config=KAPy.loadConfig()  

def getWorkflow(config):
    '''
    Get Workflow setup 
    
    Generates a series of dicts describing the workflow dependencies of this configuration
    '''
    #Extract specific configurations 
    inp=config['inputs']
    sc=config['scenarios']
    
    #Primary Variables-----------------------------------------------------------------------
    #PVs are the raw inputs. These need to be read into a single-file format based on 
    #xarray, and are then exported either as netcdf or as pickles.
    
    #Reshape the input structure into a more workable format, including
    #the addition of a list of files
    inpDict={}
    thisKey=0
    for thisInp in inp.keys():
        for thisVar in inp[thisInp].keys():
            #Get file list
            theseFiles=glob.glob(KAPy.buildPath(config,'inputs',inp[thisInp][thisVar]['path']))
            #Write back into input list
            thisKey+=1
            inpDict[thisKey]={}
            inpDict[thisKey]['varName']=thisVar
            inpDict[thisKey]['src']=thisInp
            inpDict[thisKey].update(inp[thisInp][thisVar])
            inpDict[thisKey]['files']=theseFiles
    
    #Make into table, extract stems and prepare for matching
    inpTbl= pd.DataFrame.from_dict(inpDict,orient='index').explode('files')
    inpTbl['stems']=inpTbl['files'].str.extract('^(.*)_.*$') #TODO: Use regex stem

    #Now loop over the scenario definitions to get the list
    pvList=[]
    for thisSc in sc.values():
        #Get files that match experiments
        matchPat='|'.join([f'_{x}_' for x in thisSc['experiments']])
        inSc=inpTbl['stems'].str.contains(matchPat)
        theseFiles=inpTbl[inSc].copy() #Explicit copy to avoid SettingWithCopyWarning
        #Generate the primary variable filename
        pvFname=[re.sub(matchPat,'_',os.path.basename(x))
                               for x in theseFiles['stems']]
        theseFiles['pvFname']=theseFiles['varName']+"_" + theseFiles['src'] + "_" + thisSc['shortname'] + "_" + pvFname  
        pvList+=[theseFiles]
    pvTbl=pd.concat(pvList) 
    #Build the full filename
    if config['primVars']['storeAsNetCDF']:
        pvTbl['pvFname']=pvTbl['pvFname']+'.nc'  #Store as NetCDF
    else:
        pvTbl['pvFname']=pvTbl['pvFname']+'.pkl' #Pickle

    #tidy up the output into a dict
    pvDict=pvTbl.groupby("pvFname").apply(lambda x:list(x['files'])).to_dict()
    
    #Indicators -----------------------------------------------------
    ind=config['indicators']
    #Combine all variable tables (e.g. prim, sec, bc, tert)
    varTbl=pvTbl[['varName','src','pvFname']].drop_duplicates()
    varTbl=varTbl.rename(columns={'pvFname':'varFname'})
    varTbl['varPath']=KAPy.buildPath(config,'primVars')
    varTbl['varPath']=varTbl['varPath']+os.path.sep +varTbl['varFname']
    #Loop over indicators and get required files
    #Currently only matching one variable. TODO: Add multiple
    for indKey, indVal in ind.items():
        #useThis=varTbl['varName'].isin([indVal['variables']])
        useThese=varTbl['varName'] == indVal['variables']
        ind[indKey]['varPath']=varTbl['varPath'][useThese]
    #Now extract the dict
    indTbl=pd.DataFrame.from_dict(ind,orient='index').explode('varPath')
    indTbl['varFname']=[os.path.basename(f) for f in indTbl['varPath']]
    indTbl['indFname']= indTbl.apply(lambda x: f'i{x["id"]}_'+re.sub("^(.*?)_","",x['varFname']),
                                    axis=1)
    indDict=indTbl.groupby("id").apply(lambda x: [x]).to_dict() 
    for key in indDict.keys():
        indDict[key]=indDict[key][0].groupby("indFname").apply(lambda x:list(x['varPath'])).to_dict()
    
        
    #Finish--------------------------------------------------------
    rtn={'primVars':pvDict,
         'indicators':indDict}
    return(rtn)


