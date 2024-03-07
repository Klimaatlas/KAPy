#Given a set of input files, create datachunk objects that can be worked with

import pandas as pd
import os
import sys
import glob
import re

"""
#Setup for debugging with a Jupyterlab console
import os
os.chdir("..")
import KAPy
os.chdir("..")
config=KAPy.loadConfig()  
"""

def getWorkflow(config):
    '''
    Get Workflow setup 
    
    Generates a series of dicts describing the workflow dependencies of this configuration
    '''
    #Extract specific configurations 
    inp=config['inputs']
    sc=config['scenarios']
    outDirs=config['dirs']
    
    #Primary Variables ---------------------------------------------------------------
    #PVs are the raw inputs. These need to be read into a single-file format based on 
    #xarray, and are then exported either as netcdf or as pickles.
    #Add list of files to the input dictioanry
    for thisKey,thisInp in inp.items():
        #Get file list
        theseFiles=glob.glob(thisInp['path'])
        #Write filelist back into input list
        inp[thisKey]['inpPath']=theseFiles
    
    #Make into table and extract stems 
    inpTbl= pd.DataFrame.from_dict(inp,orient='index').explode('inpPath')
    inpTbl['stems']=[re.search(x['regex'],os.path.basename(x['inpPath'])).group(1) 
                      for i,x in inpTbl.iterrows()] 
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
        theseFiles['pvFname']=theseFiles['varName']+"_" + theseFiles['srcName'] + \
                                "_" + thisSc['shortname'] + "_" + pvFname  
        pvList+=[theseFiles]
    pvTbl=pd.concat(pvList) 
    pvTbl['pvPath']=[os.path.join(outDirs['primVars'],f)
                     for f in pvTbl['pvFname']]
    #Build the full filename
    if config['primVars']['storeAsNetCDF']:
        pvTbl['pvPath']=pvTbl['pvPath']+'.nc'  #Store as NetCDF
    else:
        pvTbl['pvPath']=pvTbl['pvPath']+'.pkl' #Pickle

    #tidy up the output into a dict
    pvDict=pvTbl.groupby("pvPath").apply(lambda x:list(x['inpPath']),
                                         include_groups=False).to_dict()
    
    #Indicators -----------------------------------------------------
    ind=config['indicators']
    #Combine all variable tables (e.g. prim, sec, bc, tert)
    varPalette=[pvDict]
    varTbl=pd.DataFrame([thisKey 
                         for varDict in varPalette 
                         for thisKey in varDict.keys() ],
                       columns=["varPath"])
    varTbl['varFname']=[os.path.basename(p) for p in varTbl['varPath']]
    varTbl['varName']=varTbl['varFname'].str.extract('^(.*?)_.*$')
    varTbl['src']=varTbl['varFname'].str.extract('^.*?_(.*?)_.*$')
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
    indTbl['indPath']= [os.path.join(outDirs['indicators'],f) 
                          for f in indTbl['indFname']]
    indDict=indTbl.groupby("id").apply(lambda x: [x],include_groups=False).to_dict() 
    for key in indDict.keys():
        indDict[key]=indDict[key][0].groupby("indPath").apply(lambda x:list(x['varPath']),
                                                              include_groups=False).to_dict()
    
    #Ensembles-------------------------------------
    #Build ensemble membership
    ensTbl=pd.DataFrame([i for this in indDict.values() for i in this.keys() ],
                        columns=["indPath"])
    ensTbl['indFname']=[os.path.basename(p) for p in ensTbl['indPath']]
    ensTbl['ens']=ensTbl['indFname'].str.extract("(.*?_.*?_.*?)_.*$")
    ensTbl['ensPath']=[os.path.join(outDirs["ensstats"],f+"_ensstats.nc")
                        for f in ensTbl['ens']]
    #Extract the dict
    ensDict=ensTbl.groupby("ensPath").apply(lambda x:list(x['indPath']),
                                            include_groups=False).to_dict()
    
    #Arealstatistics----------------------------------------------
    #Start by building list of input files to calculate arealstatistics for
    asInps=list(ensDict.keys())
    if config['arealstats']['calcForMembers']:
        asInps+=[y for x in ensDict.values() for y in x]
    asTbl=pd.DataFrame(asInps,columns=['srcPath'])
    #Now setup output structures
    asTbl['srcFname']=[os.path.basename(p) for p in asTbl['srcPath']]
    asTbl['asFname']=asTbl['srcFname'].str.replace('nc','csv')
    asTbl['asPath']=[os.path.join(outDirs['arealstats'],f)
                     for f in asTbl['asFname']]
    #Make the dict
    asDict=asTbl.groupby("asPath").apply(lambda x:list(x['srcPath']),
                                         include_groups=False).to_dict()
    
    #Notebooks----------------------------------------------------
    #This is easy - notebooks need everything in ensstats and arealstats
    nbInps=list(ensDict.keys())+list(asDict.keys())
    if isinstance(config['notebooks'],str):
        nbTbl=pd.DataFrame([config['notebooks']],columns=['nbPath'])
    else:
        nbTbl=pd.DataFrame(config['notebooks'],columns=['nbPath'])
    nbTbl['nbFname']=[os.path.basename(f) for f in nbTbl['nbPath']]
    nbTbl['htmlFname']=nbTbl['nbFname'].str.replace(".ipynb",".html")
    nbTbl['htmlPath']=[os.path.join(outDirs['notebooks'],f)
                       for f in nbTbl['htmlFname']]
    nbDict={r['htmlPath']: [r['nbPath']] + nbInps for i,r in nbTbl.iterrows()}
    
    #Collate and round off--------------------------------------------------------
    rtn={'primVars':pvDict,
         'indicators':indDict,
        'ensstats':ensDict,
        'arealstats':asDict,
        'notebooks':nbDict}
    #Need to create an "all" dict as well containing all targets in the workflow
    allList=[]
    for k,v in rtn.items():
        if k=='indicators':  #Requires special handling, as it is a nested list
            for x in v.values():
                allList+=x.keys()
        else:
            allList+=v.keys()
    rtn['all']=allList
    
    #Fin-----------------------------------
    return(rtn)


