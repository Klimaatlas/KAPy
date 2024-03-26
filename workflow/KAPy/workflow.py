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

def filelistToDataframe(flist):
        #Converts a list of file paths to a dataframe, with metadata extract
        thisTbl=pd.DataFrame(flist,columns=['path'])
        thisTbl['fname']=[os.path.basename(p) for p in thisTbl['path']]
        thisTbl['varName']=thisTbl['fname'].str.extract('^(.*?)_.*$')
        thisTbl['src']=thisTbl['fname'].str.extract('^.*?_(.*?)_.*$')
        thisTbl['stems']=thisTbl['fname'].str.extract('^.*?_.*?_(.*).(?:nc|pkl)$')
        return(thisTbl)

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
        pvTbl['pvPath']=[os.path.join(outDirs['variables'],thisInp['varName'],f)
                         for f in pvTbl['pvFname']]
        if config['primVars']['storeAsNetCDF']:
            pvTbl['pvPath']=pvTbl['pvPath']+'.nc'  #Store as NetCDF
        else:
            pvTbl['pvPath']=pvTbl['pvPath']+'.pkl' #Pickle

        pvDict[thisKey]=pvTbl.groupby("pvPath").apply(lambda x:list(x['inpPath']),
                                             include_groups=False).to_dict()

    #Secondary Variables---------------------------------------------
    #Setup the variable palette. As we add each addition variable, we concatentate it onto
    #the variable palette
    varList=[k for v in pvDict.values() for k in v.keys() ]
    svDict={}
    #Iterate over secondary variables if they are request
    if 'secondaryVars' in config:
        for thisSV in config['secondaryVars'].values():
            #Convert varList into a workable format
            varTbl=filelistToDataframe(varList)
            #Now filter by the input variables needed for this derived variable
            selThese=[v in thisSV['inputVars'] for v in varTbl['varName'] ]
            longSVTbl=varTbl[selThese]
            try:
                if longSVTbl.size==0:
                    raise ValueError(f"Cannot find any matching input files for {thisSV['name']}. Check the definition again. Also check the order of definition.")
            except ValueError as e:
                print("Error:",e)

            #Pivot and retain only those in common
            svTbl=longSVTbl.pivot(index=['src','stems'],
                                columns='varName',
                                values='path')
            svTbl=svTbl.dropna().reset_index()
            #Now we have a list of valid files that can be made. Store the results
            validPaths=[os.path.join(outDirs['variables'],
                                     var,fName)
                         for var in thisSV['outputVars']
                         for fName in f"{var}_"+svTbl['src']+"_"+svTbl['stems']+".nc"] 

            svDict[thisSV['id']]=thisSV
            svDict[thisSV['id']]['files']=validPaths
            varList+=validPaths
        
    #Indicators -----------------------------------------------------
    #Get the full variable palette from varList
    varPal =filelistToDataframe(varList)
    #Loop over indicators and get required files
    #Currently only matching one variable. TODO: Add multiple
    indDict={}
    for indKey, thisInd in ind.items():
        useThese=varPal['varName'] == thisInd['variables']
        selVars=varPal[useThese]
        validPaths=[os.path.join(outDirs['indicators'],
                                str(thisInd['id']),fName)
                     for fName in f"{thisInd['id']}_"+selVars['src']+"_"+selVars['stems']+".nc"] 
        indDict[indKey]=thisInd
        indDict[indKey]['files']=validPaths
    
    #Regridding-----------------------------------------------------------------------
    #We only regrid if it is requested in the configuration
    doRegridding= (config['outputGrid']['regriddingEngine']!='None')
    if doRegridding:
        #Remap directory
        rgTbl=pd.DataFrame([i for this in indDict.values() for i in this['files']],
                            columns=["indPath"])
        rgTbl['indID']=[os.path.basename(os.path.dirname(f)) for f in rgTbl['indPath']]
        rgTbl['indFname']=[os.path.basename(p) for p in rgTbl['indPath']]
        rgTbl['rgPath']=[os.path.join(outDirs["regridded"],f) for f in rgTbl['indFname']]
        validPaths=[os.path.join(outDirs['regridded'],
                                rw['indID'],rw['indFname'])
                     for idx,rw in rgTbl.iterrows()] 
        #Extract the dict
        rgDict={'files' : validPaths}
    else:
        rgDict={'files': []}

        
    #Ensembles----------------------------------------------------------------------------
    #Build ensemble membership - the exact source here depends on whether
    #we are doing regridding or not
    if doRegridding:
        ensTbl=pd.DataFrame(rgDict['files'],columns=["srcPath"])
    else:
        ensTbl=pd.DataFrame([i for this in indDict.values() for i in this['files'] ],
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
         'secondaryVars': svDict,
         'indicators':indDict,
         "regridded": rgDict,
        'ensstats':ensDict,
        'arealstats':asDict,
        'notebooks':nbDict}
    #Need to create an "all" dict as well containing all targets in the workflow
    allList=[]
    for k,v in rtn.items():
        if k in ['primVars']:  #Requires special handling, as these are nested lists
            for x in v.values():
                allList+=x.keys()
        elif k in ['secondaryVars','indicators']:  #Requires special handling, as these are nested lists
            for x in v.values():
                allList+=x['files']
        elif k in ['regridded']:  #Requires special handling, as these are nested lists
                allList+=v['files']
        else:
            allList+=v.keys()
    rtn['all']=allList
    
    #Fin-----------------------------------
    return(rtn)


