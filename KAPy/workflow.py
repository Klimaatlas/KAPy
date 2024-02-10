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
    ind=config['indicators']
    
    #Chunks-----------------------------------------------------------------------
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
    inpTbl['stems']=inpTbl['files'].str.extract('^(.*)_.*$') 

    #Now loop over the scenario definitions to get the list
    chList=[]
    for thisSc in sc.values():
        #Get files that match experiments
        matchPat='|'.join([f'_{x}_' for x in thisSc['experiments']])
        inSc=inpTbl['stems'].str.contains(matchPat)
        theseFiles=inpTbl[inSc].copy() #Explicit copy to avoid SettingWithCopyWarning
        #Generate the datachunk filename
        chFname=[re.sub(matchPat,'_',os.path.basename(x))
                               for x in theseFiles['stems']]
        theseFiles['chFname']=theseFiles['varName']+"_" + theseFiles['src'] + "_" + thisSc['shortname'] + "_" + chFname  
        chList+=[theseFiles]
    chTbl=pd.concat(chList) 
    #Build the full filename
    if config['chunks']['storeAsNetCDF']:
        chTbl['chFname']=chTbl['chFname']+'.nc'  #Store as NetCDF
    else:
        chTbl['chFname']=chTbl['chFname']+'.pkl' #Pickle

    #tidy up the output into a dict
    chDict=chTbl.groupby("chFname").apply(lambda x:list(x['files'])).to_dict()
    
    #Indicators -----------------------------------------------------
    #Simplify chunklist 
    '''   
    #Loop over indicators and get required files
    for indKey, indValues in ind.items():
        #Get the datachunks
        ind[indKey]
    '''    

    #Finish--------------------------------------------------------
    rtn={'chunks':chDict}
    return(rtn)


