#Given a set of input files, create datachunk objects that can be worked with

"""
#Setup for debugging with a Jupyterlab console
import os
os.chdir("..")
import KAPy
os.chdir("..")
config=KAPy.loadConfig()  
"""

import pandas as pd
import os
import sys
import glob
import re


def getWorkflow(config):
    '''
    Get Workflow setup 
    
    Generates a series of dicts describing the workflow dependencies of this configuration
    '''
    #Extract specific configurations 
    inp=config['inputs']
    ind=config['indicators']
    sc=config['scenarios']
    outDirs=config['dirs']
    
    #Primary Variables ---------------------------------------------------------------
    #PVs are the raw inputs. These need to be read into a single-file format based on 
    #xarray, and are then exported either as netcdf or as pickles.
    #We loop over the individual items maintaining the dict format, as this is a touch easier to
    #work with
    pvDict={}
    for thisKey,thisInp in inp.items():
        #Get file list
        inpTbl=pd.DataFrame(glob.glob(thisInp['path']),columns=['inpPath'])
        #Make into table and extract stems 
        inpTbl['stems']=[re.search(thisInp['regex'],os.path.basename(x)).group(1)
                          for x in inpTbl['inpPath']] 
        #Process inputs that have scenarios first
        pvList=[]
        if thisInp['hasScenarios']:
            for thisSc in sc.values():
                #Get files that match experiments
                inSc=inpTbl['stems'].str.contains(thisSc['regex'])
                theseFiles=inpTbl[inSc].copy() #Explicit copy to avoid SettingWithCopyWarning
                #Generate the primary variable filename
                theseFiles['pvFname']=[re.sub(thisSc['regex'],'',os.path.basename(x))
                                       for x in theseFiles['stems']]
                theseFiles['pvFname']=f"{thisInp['varName']}_{thisInp['srcName']}_{thisSc['id']}_" + \
                                    theseFiles['pvFname']
                pvList+=[theseFiles]
        else:
            inpTbl['pvFname']=f"{thisInp['varName']}_{thisInp['srcName']}_"+ inpTbl['stems']
            pvList+=[inpTbl]
        
        #Build the full filename and tidy up the output into a dict
        pvTbl=pd.concat(pvList) 
        pvTbl['pvPath']=[os.path.join(outDirs['primVars'],f)
                         for f in pvTbl['pvFname']]
        if config['primVars']['storeAsNetCDF']:
            pvTbl['pvPath']=pvTbl['pvPath']+'.nc'  #Store as NetCDF
        else:
            pvTbl['pvPath']=pvTbl['pvPath']+'.pkl' #Pickle

        pvDict[thisKey]=pvTbl.groupby("pvPath").apply(lambda x:list(x['inpPath']),
                                             include_groups=False).to_dict()
    
    #Indicators -----------------------------------------------------
    #Combine all variable tables (e.g. prim, sec, bc, tert)
    #Indicators need to check whether a variable requested exists
    varPalette=[v for v in pvDict.values()]
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
    indTbl['indFname']= indTbl.apply(lambda x: f'{x["id"]}_'+re.sub("^(.*?)_","",x['varFname']),
                                    axis=1)
    indTbl['indPath']= [os.path.join(outDirs['indicators'],f) 
                          for f in indTbl['indFname']]
    indDict=indTbl.groupby("id").apply(lambda x: [x],include_groups=False).to_dict() 
    for key in indDict.keys():
        indDict[key]=indDict[key][0].groupby("indPath").apply(lambda x:list(x['varPath']),
                                                              include_groups=False).to_dict()
    
    #Regridding-----------------------------------------------------------------------
    #We only regrid if it is requested in the configuration
    doRegridding= (config['outputGrid']['regriddingEngine']!='None')
    rgDict={}
    if doRegridding:
        #Remap directory
        rgTbl=pd.DataFrame([i for this in indDict.values() for i in this.keys() ],
                            columns=["indPath"])
        rgTbl['indFname']=[os.path.basename(p) for p in rgTbl['indPath']]
        rgTbl['rgPath']=[os.path.join(outDirs["regridded"],f) for f in rgTbl['indFname']]
        #Extract the dict
        rgDict=rgTbl.groupby("rgPath").apply(lambda x:list(x['indPath']),
                                                include_groups=False).to_dict()
    
    #Ensembles----------------------------------------------------------------------------
    #Build ensemble membership - the exact source here depends on whether
    #we are doing regridding or not
    if doRegridding:
        ensTbl=pd.DataFrame(rgDict.keys(),columns=["srcPath"])
    else:
        ensTbl=pd.DataFrame([i for this in indDict.values() for i in this.keys() ],
                            columns=["srcPath"])
    ensTbl['srcFname']=[os.path.basename(p) for p in ensTbl['srcPath']]
    ensTbl['ens']=ensTbl['srcFname'].str.extract("(.*?_.*?_.*?)_.*$")
    ensTbl['ensPath']=[os.path.join(outDirs["ensstats"],f+"_ensstats.nc")
                        for f in ensTbl['ens']]
    #Extract the dict
    ensDict=ensTbl.groupby("ensPath").apply(lambda x:list(x['srcPath']),
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
         "regridded": rgDict,
        'ensstats':ensDict,
        'arealstats':asDict,
        'notebooks':nbDict}
    #Need to create an "all" dict as well containing all targets in the workflow
    allList=[]
    for k,v in rtn.items():
        if k in ['primVars','indicators']:  #Requires special handling, as it is a nested list
            for x in v.values():
                allList+=x.keys()
        else:
            allList+=v.keys()
    rtn['all']=allList
    
    #Fin-----------------------------------
    return(rtn)


