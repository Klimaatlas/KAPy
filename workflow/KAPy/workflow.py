"""
#Setup for debugging with VS Code 
import os
print(os.getcwd())
os.chdir("KAPy/workflow")
import KAPy
os.chdir("../..")
config=KAPy.getConfig("./config/config.yaml")
pd.set_option('display.max_colwidth', None)
"""

import sys
import os
import pandas as pd
import glob

def getWorkflow(config):
    """
    Get Workflow setup

    Generates a description of the workflow dependencies of this configuration
    """
    # Extract specific configurations
    inp = config["inputs"]
    ind = config["indicators"]
    outDirs = config["dirs"]

    # Primary Variables ---------------------------------------------------------------
    # PVs are the raw inputs. These need to be read into a single-file format based on
    # xarray, and are then exported either as netcdf or as pickles.
    # We loop over the individual items maintaining the dict format, as this is a touch easier to
    # work with
    pvDict = {}
    for thisKey, thisInp in inp.items():
        # Get file list
        inpTbl = pd.DataFrame(sorted(glob.glob(thisInp["path"])), columns=["inPath"])
        inpTbl['inFname']=[os.path.basename(p) for p in inpTbl['inPath']]
        #First, handle case where we don't find any files. We could ignore it,
        # but it's best to throw an error
        if len(inpTbl)==0:
            raise FileNotFoundError(f'No files found for input path "{thisInp["path"]}"')
        
        # If we only get one file, then there's not really much to do - that file
        # is the only member of the ensemble and we use it more or less directly
        # Handle that case first.
        elif len(inpTbl)==1:
            #Set output filename, setting the file extension manually.
            pvTbl=inpTbl
            pvTbl['pvFname']= \
                    f"{thisInp['varCode']}_{thisInp['datasetCode']}_{thisInp['gridCode']}_noExpt_noEnsID.nc"

        # A similar case also exists where there is a single ensemble member, but it
        # is spread across multiple files. This is indicated when the ensMemberFields and 
        # experimentField is empty. We handle all variates of that here
        elif thisInp['ensMemberFields']==[''] and thisInp['experimentField']=='' and len(inpTbl)>1:
            pvTbl=inpTbl
            pvTbl['pvFname']= \
                    f"{thisInp['varCode']}_{thisInp['datasetCode']}_{thisInp['gridCode']}_noExpt_noEnsID.nc"
        # elif thisInp['ensMemberFields']==['']:
        #     raise ValueError("Unhandled case. Please file a bug")
        # elif thisInp['experimentField']==['']:
        #     raise ValueError("Unhandled case. Please file a bug")
        # Else multiple hits detected that need to be handled.
        else:
            # Handling multiple files requires some information from the filenames, 
            # and therefore the fieldSeparator needs to be defined. If not, throw an error
            if thisInp['fieldSeparator']=='':
                raise ValueError(f'fieldSeparator is not defined for "{thisInp['varCode']}-{thisInp['datasetCode']}" ' + \
                         f'but {len(inpTbl)} files were detected.')

            # Split filenames into columns and extract predefined elements
            inpTbl['split']=inpTbl['inFname'].str.split(thisInp['fieldSeparator'])
            inpTbl['experiment']=[f[int(thisInp['experimentField'])-1] for f in inpTbl['split']]
            ensMemberFieldsIdxs = [int(i)-1 for i in thisInp['ensMemberFields']]
            inpTbl['ensMemberID']=["_".join([f[i] for i in ensMemberFieldsIdxs]) for f in inpTbl['split']]

            # Deal with the issue around the definition of a common experiment
            if thisInp["commonExperiment"]=='':
                #If a commonExperiment is not defined, then we just handle each
                #experiment individually
                #Form the corresponding filename. Don't forget to add the .nc
                inpTbl['pvFname']= \
                    f"{thisInp['varCode']}_{thisInp['datasetCode']}_{thisInp['gridCode']}_" + \
                    inpTbl['experiment'] + "_" + \
                    inpTbl['ensMemberID'] +".nc"

                # Store results
                pvTbl = inpTbl[['pvFname','inPath']]

            # Else, handle the more complex case where we have defined a common experiment
            else:
                #Split table into commonExperiment and other Experiments
                commonExptTable=inpTbl[inpTbl['experiment'].isin([thisInp['commonExperiment']])].copy()
                otherExptTable=inpTbl[~inpTbl['experiment'].isin([thisInp['commonExperiment']])]

                #Get list of other experiments
                otherExptList=otherExptTable['experiment'].unique()

                #Setup storage and  loop over the experiments
                pvList = []
                for thisExpt in otherExptList:
                    # Get files that are either in the experiment of interest first
                    theseExptFiles=inpTbl[inpTbl['experiment'].isin([thisExpt])].copy()

                    #Forming the corresponding filenames. Don't forget to add the .nc
                    #Experiment naming is the sum of the commonExpt and thisExpt
                    theseExptFiles['pvFname']= \
                        f"{thisInp['varCode']}_{thisInp['datasetCode']}_{thisInp['gridCode']}" + \
                        f"_{thisInp["commonExperiment"]}+{thisExpt}_" + \
                        theseExptFiles['ensMemberID'] +".nc"
                    commonExptTable['pvFname']= \
                        f"{thisInp['varCode']}_{thisInp['datasetCode']}_{thisInp['gridCode']}" + \
                        f"_{thisInp["commonExperiment"]}+{thisExpt}_" + \
                        commonExptTable['ensMemberID'] +".nc"
                    
                    #Now select the files from the commonExpt that are also in the
                    #otherExperiment table. This makes sure that we only add
                    #commonExpt ensemble members that have corresponding files
                    #in the given experiment (thisExpt). Then concat. Throw an
                    #error if none found
                    theseCommonExptFiles=commonExptTable[
                        commonExptTable['pvFname'].isin(theseExptFiles['pvFname'])
                    ]
                    if theseCommonExptFiles.shape[0]==0:
                        raise ValueError(f"Cannot find commonExperiment files to match '{theseExptFiles['inPath'].iloc[0]}'.")

                    combinedFileTbl=pd.concat([theseCommonExptFiles,theseExptFiles,])

                    # Store results
                    pvList += [combinedFileTbl[['pvFname','inPath']]]
                
                #Concatenate into the final table
                pvTbl = pd.concat(pvList)

        # Build the full filename and tidy up the output into a dict
        pvTbl["pvPath"] = [
            os.path.join(outDirs["primaryVariables"], thisKey, f)
            for f in pvTbl["pvFname"]
        ]

        # If we're pickling, name the output files accordingly
        if config['processing']['picklePrimaryVariables']:
            pvTbl["pvPath"] = pvTbl["pvPath"] + ".pkl"
        
        #Prior to adding to the pvDict, check that we have unique keys
        if any(pvTbl['pvPath'].isin(pvDict.keys())):
            raise ValueError("Duplicate keys found in generating primary variables.")

        #Finally, make the dict
        pvDict[thisKey] =(
            pvTbl.groupby("pvPath")
            .apply(lambda x: list(x["inPath"]), include_groups=False)
            .to_dict()
        )

    # Secondary Variables---------------------------------------------
    # Setup the variable palette as a tabular list of files. As we add each
    # additional variable, we concatentate it onto the variable palette.
    def parseFilelist(flist):
        thisTbl = pd.DataFrame(flist,columns=["path"])
        thisTbl["fname"] = [os.path.basename(p) for p in thisTbl["path"]]
        thisTbl["var"] = thisTbl["fname"].str.extract("^([^_]+)_.*$")
        thisTbl["dataset"] = thisTbl["fname"].str.extract("^[^_]+_([^_]+)_.*$")
        thisTbl["grid"] = thisTbl["fname"].str.extract("^[^_]+_[^_]+_([^_]+)_.*$")
        thisTbl["expt"] = thisTbl["fname"].str.extract("^[^_]+_[^_]+_[^_]+_([^_.]+).*$")
        thisTbl["stems"] = thisTbl["fname"].str.extract("^[^_]+_[^_]+_[^_]+_[^_]+_(.+).nc(?:.pkl)?$")
        return thisTbl

    varPal = parseFilelist([k for v in pvDict.values() for k in v.keys()])

    # Iterate over secondary variables if they are request
    svDict = {}
    if "secondaryVars" in config:
        for thisKey,thisSV in config["secondaryVars"].items():
            # Now filter by the input variables needed for this derived variable
            selThese = [v in thisSV["inputVars"] for v in varPal["var"]]
            longSVTbl = varPal[selThese]
            if longSVTbl.size == 0:
                    raise ValueError(f"Cannot find any input variables for {thisSV['id']}. ")

            # Pivot and retain only those in common
            svTbl = longSVTbl.pivot(
                index=["dataset","grid","expt", "stems"], columns="var", values="path"
            )
            svTbl = svTbl.dropna().reset_index()
            if svTbl.size == 0:
                raise ValueError(f"Cannot find any matching input variables for {thisSV['id']}. ")

            # Now we have a list of valid files that can be made. Store the results
            svTbl['outFile'] = [
                os.path.join(outDirs["secondaryVariables"], thisKey, fName)
                for fName in f"{thisSV["outputVars"][0]}_" + svTbl["dataset"] + "_" + svTbl['grid']+"_"+svTbl["expt"]+"_"+svTbl["stems"]+".nc"
            ]

            # Add to output dict
            outDict={}
            for idx, rw in svTbl.iterrows():
                inputVarDict={v:rw[v] for v in thisSV['inputVars']}
                outDict[rw['outFile']] =inputVarDict 
            svDict[thisSV['id']] = outDict

            # Add to variable palette
            varPal = pd.concat([varPal,
                               parseFilelist(svTbl['outFile'].to_list())])

    # Bias Adjustment -------------------------------------------------------
    # Bias adjusted variables and secondary variables share a very similar logic
    # They only kick in if requested, draw upon the variable palette, and feed back
    # into when complete
    BADict = {}
    # Iterate over secondary variables if they are request
    if "biasAdjustment" in config:
        for thisKey,thisBA in config["biasAdjustment"].items():
            # Now filter by the input variables needed for this bias adjustment 
            selThese = (varPal["var"] ==thisBA['baVariable']) & \
                        (varPal["dataset"]==thisBA['targetDataset'])
            BAtbl = varPal[selThese].copy()
            try:
                if BAtbl.size == 0:
                    raise ValueError(
                        f"Cannot find any matching input files for {thisBA['id']}. "
                        + "Check the definition again. Also check the order of definition."
                    )
            except ValueError as e:
                print("Error:", e)

            # The workflow also requires that the reference dataset is present, so this becomes
            # a prerequisite for making the output
            selThese = (varPal["var"] ==thisBA['baVariable']) & \
                        (varPal["dataset"]==thisBA['refDataset'])
            if sum(selThese)!=1:
                raise ValueError("Cannot find a unique data variable to use as the reference "
                                 + f'for bias adjustment of "{thisBA['baVariable']}_{thisBA['targetDataset']}"')
            refDict = varPal[selThese].to_dict(orient="records")[0]

            # Now we have a list of valid files that can be made. Store the results
            BAtbl['outFile'] = [
                os.path.join(outDirs["biasAdjustment"], thisKey, fName)
                for fName in f"{thisBA["baVariable"]}_" + thisBA["outDatasetCode"] + "_" + refDict['grid']+"_"+BAtbl["expt"]+"_"+BAtbl["stems"]+".nc"
            ]

            # Add to output dict
            outDict={}
            for idx, rw in BAtbl.iterrows():
                outDict[rw['outFile']] = {'histsim':rw['path'],'ref':refDict['path']}
            BADict[thisBA['id']]=outDict

            # Add to variable palette
            varPal = pd.concat([varPal,
                               parseFilelist(BAtbl['outFile'].to_list())])


    # Tertiary Variables---------------------------------------------
    # Iterate over tertiary variables if they are requested. The approach
    # here is very similar to secondary variables, but we only draw on
    # the variables in the post-BA palette (postBAPal) instead of the full variable
    # palette. Ideally this should be merged into a function.
    # Note that tertiary variables can only be created if there are bias adjusted variables 
    # created first
    tvDict = {}
    if ("tertiaryVars" in config) and ("biasAdjustment" in config):
        postBAPal = parseFilelist([k for v in BADict.values() for k in v.keys()])
        for thisKey,thisTV in config["tertiaryVars"].items():
            # Filter by the input variables needed for this derived variable
            selThese = [v in thisTV["inputVars"] for v in postBAPal["var"]]
            longTVTbl = postBAPal[selThese]
            if longTVTbl.size == 0:
                    raise ValueError(f"Cannot find any input variables for tertiary variable '{thisTV['id']}'. ")

            # Pivot and retain only those in common
            tvTbl = longTVTbl.pivot(
                index=["dataset","grid","expt", "stems"], columns="var", values="path"
            )
            tvTbl = tvTbl.dropna().reset_index()
            if tvTbl.size == 0:
                raise ValueError(f"Cannot find matching input variables for tertiary variable '{thisTV['id']}'. ")

            # Now we have a list of valid files that can be made. Store the results
            tvTbl['outFile'] = [
                os.path.join(outDirs["tertiaryVariables"], thisKey, fName)
                for fName in f"{thisTV["outputVars"][0]}_" + tvTbl["dataset"] + "_" + tvTbl['grid']+"_"+tvTbl["expt"]+"_"+tvTbl["stems"]+".nc"
            ]

            # Add to output dict
            outDict={}
            for idx, rw in tvTbl.iterrows():
                inputVarDict={v:rw[v] for v in thisTV['inputVars']}
                outDict[rw['outFile']] =inputVarDict 
            tvDict[thisTV['id']] = outDict

            # Add to variable palette
            postBAPal=pd.concat([postBAPal,
                               parseFilelist(tvTbl['outFile'].to_list())])
            varPal = pd.concat([varPal,
                               parseFilelist(tvTbl['outFile'].to_list())])


    # Indicators -----------------------------------------------------
    # Loop over indicators and get required files
    # Currently only matching one variable. TODO: Allow multiple variables
    indDict = {}
    for indKey, thisInd in ind.items():
        #Build up the output filename first
        varPal['indFname']=varPal['fname'].str.replace(r"^([^_]+)_(.+?)(\.pkl)?$",
                                                       indKey+r"_\2",
                                                       regex=True)
        #Build the rest of the path
        varPal["indPath"] = [
            os.path.join(outDirs["indicators"],
                         indKey,
                         rw["indFname"])
            for idx, rw in varPal.iterrows()
        ]
        #Only extract the dict for the part that we are actually
        #interested in, including both variables and datasets
        varPal['hasVars'] = varPal["var"] == thisInd["variables"]
        varPal['correctDataset'] = [v in thisInd['datasets']  for v in varPal['dataset']]
        if "all" in thisInd['datasets']:
            useThese = varPal['hasVars']
        else:
            useThese = varPal['hasVars'] & varPal['correctDataset']
        if not any(useThese):
            raise ValueError(f"Cannot find variable(s) '{thisInd["variables"]}' for datasets '{thisInd['datasets']}' to calculate indicators from.")
        indDict[indKey] = {rw["indPath"]: [rw["path"]] \
                                    for idx, rw in varPal[useThese].iterrows()}

    # Regridding-----------------------------------------------------------------------
    # We only regrid if it is requested in the configuration
    doRegridding = config["outputGrid"]["templateType"] != "none"
    if doRegridding:
        # Remap directory
        rgTbl = pd.DataFrame([k for v in indDict.values() for k in v.keys()], 
                          columns=["indPath"])
        rgTbl["indID"] = [os.path.basename(os.path.dirname(f)) for f in rgTbl["indPath"]]
        rgTbl["indFname"] = [os.path.basename(p) for p in rgTbl["indPath"]]
        #Replace grid code in the filename with the appropriate one
        rgTbl['rgFname'] = \
            rgTbl["indFname"].str.replace(r'^([^_]+_[^_]+_)[^_]+(_.*$)',
                                        r'\1'+config['outputGrid']['gridName']+r'\2',
                                        regex=True)
        #Build the rest of the paths
        rgTbl["rgPath"] = [
            os.path.join(outDirs["regridded"], rw["indID"], rw["rgFname"])
            for idx, rw in rgTbl.iterrows()
        ]

        #Check for the presence of duplicates in rgPath. Fail if found
        if len(rgTbl['rgPath'].unique()) != len(rgTbl):
            raise ValueError("Duplicate filenames will result from the regridding step. Please recheck configuration.")
        
        # Extract the dict
        rgDict = {rw["rgPath"]: [rw["indPath"]] for idx, rw in rgTbl.iterrows()}
    else:
        rgDict = {}

    # Ensembles----------------------------------------------------------------------------
    # Build ensemble membership - the exact source here depends on whether
    # we are doing regridding or not
    if doRegridding:
        ensTbl = pd.DataFrame(rgDict.keys(), columns=["srcPath"])
    else:
        ensTbl = pd.DataFrame(
            [k for v in indDict.values() for k in v.keys()], columns=["srcPath"]
        )
    ensTbl["srcFname"] = [os.path.basename(p) for p in ensTbl["srcPath"]]
    ensTbl["ensID"] = ensTbl["srcFname"].str.extract("^([^_]+_[^_]+_[^_]+_[^_]+)_.*$")
    #Build path and extract dict
    ensTbl["ensPath"] = [
        os.path.join(outDirs["ensstats"], f + "_ensstats.nc") for f in ensTbl["ensID"]
    ]
    ensDict = (
        ensTbl.groupby("ensPath")
        .apply(lambda x: list(x["srcPath"]), include_groups=False)
        .to_dict()
    )

    # Arealstatistics----------------------------------------------
    # Start by building list of input files to calculate arealstatistics for
    # Note that we split into ensemble and member statistics
    asEnsInps = pd.DataFrame(list(ensDict.keys()),columns=['srcPath'])
    asEnsInps['type']='ensstats'
    asMemInps = pd.DataFrame([y for x in ensDict.values() for y in x],
                             columns=['srcPath'])
    asMemInps['type']='members'
    asTbl=pd.concat([asEnsInps,asMemInps])
    # Now setup output structures
    asTbl["srcFname"] = [os.path.basename(p) for p in asTbl["srcPath"]]
    asTbl["asFname"] = asTbl["srcFname"].str.replace("nc", "csv")
    asTbl["asPath"] = [os.path.join(outDirs["arealstats"], rw["type"], rw["asFname"]) \
                       for idx, rw in asTbl.iterrows()]
    # Make the dict
    asDict = (
        asTbl.groupby("asPath")
        .apply(lambda x: list(x["srcPath"]), include_groups=False)
        .to_dict()
    )

    #Separate the lists of area statistics into ensstats and members for use in
    #the database output
    mergedCSVDict= asTbl.groupby("type").apply(lambda x: list(x["asPath"]), include_groups=False).to_dict()

    # Plots----------------------------------------------------
    #Get list of areal statistics csv files (in the ensstats version)
    csvList = pd.DataFrame(list(asDict.keys()), columns=["path"])
    csvList["fname"] = [os.path.basename(f) for f in csvList["path"]]
    csvList["indId"] = csvList["fname"].str.extract("^([^_]+)_.*$")
    csvList["ensMemberID"] = csvList["fname"].str.extract("^[^_]+_[^_]+_[^_]+_[^_]+_(.+).*$")
    csvList=csvList[csvList["ensMemberID"]=='ensstats.csv']
    csvDict = (
        csvList.groupby("indId")
        .apply(lambda x: list(x["path"]), include_groups=False)
        .to_dict()
    )
    
    #And of the netcdf files
    ncList = pd.DataFrame(list(ensDict.keys()), columns=["path"])
    ncList["fname"] = [os.path.basename(f) for f in ncList["path"]]
    ncList["indId"] = ncList["fname"].str.extract("^([^_]+)_.*$")
    ncDict = (
        ncList.groupby("indId")
        .apply(lambda x: list(x["path"]), include_groups=False)
        .to_dict()
    )

    # Loop over available indicators to make plots
    pltDict = {}
    for thisInd in config["indicators"].values():
        # But what should we plot? It depends on the nature of the indicator
        # * Period-based indicators should plot the spatial map and the plots, derived
        #   from the ensemble statistics
        # * Yearly (or monthly) based indicators show a time series, also for ensemble statistcs
        if thisInd["timeBinning"] == "periods":
            # Box plot - requires ensemble csv files
            bxpFname = os.path.join(outDirs["outputs"],'plots', f"{thisInd['id']}_boxplot.png")
            pltDict[bxpFname] = csvDict[str(thisInd["id"])]

            # Spatial plot - requires ensemble netcdf files
            spFname = os.path.join(outDirs["outputs"],'plots', f"{thisInd['id']}_spatial.png")
            pltDict[spFname] = ncDict[str(thisInd["id"])]

        elif thisInd["timeBinning"] in ["years", "months"]:
            # Time series plot - requires ensemble csv files
            lpFname = os.path.join(outDirs["outputs"],'plots', f"{thisInd['id']}_lineplot.png")
            pltDict[lpFname] = csvDict[str(thisInd["id"])]

    # Collate and round off----------------------------------------------
    rtn = {
        "primVars": pvDict,
        "secondaryVars": svDict,
        "baVars":BADict,
        "tertiaryVars": tvDict,
        "indicators": indDict,
        "regridded": rgDict,
        "ensstats": ensDict,
        "arealstats": asDict,
        "mergedCSVs":mergedCSVDict,
        "plots": pltDict,
    }
    # Create an "all" dict  containing 
    # all targets in the workflow
    allList = []
    for k, v in rtn.items():
        if k in ["primVars",
                 "secondaryVars",
                 "baVars",
                 "tertiaryVars",
                 "indicators"]:  # Requires special handling, as these are nested lists
            for x in v.values():
                allList += x.keys()
        elif k in ["mergedCSVs"]:  # Skip this
            continue
        else:
            allList += v.keys()
    rtn["all"] = allList

    # Fin-----------------------------------
    return rtn
