# Given a set of input files, create datachunk objects that can be worked with

"""
#Setup for debugging with VS Code 
import os
os.chdir("..")
import KAPy
os.chdir("..")
config=KAPy.getConfig("./config/config.yaml")
thisInp=config['inputs']['CORDEX-tas']
"""

import sys
import os
import pandas as pd
import glob

def getWorkflow(config):
    """
    Get Workflow setup

    Generates a series of dicts describing the workflow dependencies of this configuration
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
        inpTbl = pd.DataFrame(glob.glob(thisInp["path"]), columns=["inPath"])
        inpTbl['inFname']=[os.path.basename(p) for p in inpTbl['inPath']]

        #First, handle case where we don't find any files. We could ignore it,
        # but it's best to throw an error
        if len(inpTbl)==0:
            sys.exit(f'No files found for input path "{thisInp["path"]}"')
        
        # If we only get one file, then there's not really much to do - we're
        # going to use that file more or less directly. Handle that case first.
        elif len(inpTbl)==1:
            #Set output filename, setting the file extension manually.
            pvTbl=inpTbl
            pvTbl['pvFname']= \
                    f"{thisInp['varID']}_{thisInp['srcID']}_native-grid_no-expt_" + \
                    os.path.splitext(pvTbl['inFname'][0])[0] + '.nc'

        # Else multiple hits detected that need to be handled.
        else:
            # Handling multiple files requires some information from the filenames, 
            # and therefore the fieldSeparator needs to be defined. If not, throw an error
            if thisInp['fieldSeparator']=='':
                sys.exit(f'fieldSeparator is not defined for "{thisInp['varID']}-{thisInp['srcID']}" ' + \
                         f'but {len(inpTbl)} files were detected.')

            # Split filenames into columns and extract predefined elements
            inpTbl['split']=inpTbl['inFname'].str.split(thisInp['fieldSeparator'])
            inpTbl['grid']=[f[int(thisInp['gridField'])-1] for f in inpTbl['split']]
            inpTbl['experiment']=[f[int(thisInp['experimentField'])-1] for f in inpTbl['split']]
            ensMemberFieldsIdxs = [int(i)-1 for i in thisInp['ensMemberFields']]
            inpTbl['ensMemberID']=["_".join([f[i] for i in ensMemberFieldsIdxs]) for f in inpTbl['split']]

            # Deal with the issue around the definition of a common experiment
            if thisInp["commonExperimentID"]=='':
                #If a commonExperiment is not defined, then we just handle each
                #experiment individually
                #Form the corresponding filename. Don't forget to add the .nc
                inpTbl['pvFname']= \
                    f"{thisInp['varID']}_{thisInp['srcID']}_" + \
                    inpTbl['grid'] +"_" + inpTbl['experiment'] + "_" + \
                    inpTbl['ensMemberID'] +".nc"

                # Store results
                pvTbl = inpTbl[['pvFname','inPath']]

            # Else, handle the more complex case where we have defined a common experiment
            else:
                #Split table into commonExperiment and other Experiments
                commonExptTable=inpTbl[inpTbl['experiment'].isin([thisInp['commonExperimentID']])].copy()
                otherExptTable=inpTbl[~inpTbl['experiment'].isin([thisInp['commonExperimentID']])]

                #Get list of other experiments
                otherExptList=otherExptTable['experiment'].unique()

                #Setup storage and  loop over the experiments
                pvList = []
                for thisExpt in otherExptList:
                    # Get files that are either in the experiment of interest first
                    theseExptFiles=inpTbl[inpTbl['experiment'].isin([thisExpt])].copy()

                    #Forming the corresponding filename. Don't forget to add the .nc
                    theseExptFiles['pvFname']= \
                        f"{thisInp['varID']}_{thisInp['srcID']}_" + \
                        theseExptFiles['grid'] +"_" + thisExpt + "_" + \
                        theseExptFiles['ensMemberID'] +".nc"
                    
                    #Now do the same for the commonExpt - using the experiment
                    #naming from thisExpt (and not the native commonExperimentID)
                    commonExptTable['pvFname']= \
                        f"{thisInp['varID']}_{thisInp['srcID']}_" + \
                        commonExptTable['grid'] +"_" + thisExpt + "_" + \
                        commonExptTable['ensMemberID'] +".nc"
                    
                    #Now select the files from the commonExpt that are also in the
                    #otherExperiment table. This makes sure that we only add
                    #commonExpt ensemble members that have corresponding files
                    #in the given experiment (thisExpt). Then concat.
                    theseCommonExptFiles=commonExptTable[
                        commonExptTable['pvFname'].isin(theseExptFiles['pvFname'])
                    ]
                    combinedFileTbl=pd.concat([theseExptFiles,theseCommonExptFiles])

                    # Store results
                    pvList += [combinedFileTbl[['pvFname','inPath']]]
                
                #Concatenate into the final table
                pvTbl = pd.concat(pvList)

        # Build the full filename and tidy up the output into a dict
        pvTbl["pvPath"] = [
            os.path.join(outDirs["variables"], thisInp["varID"], f)
            for f in pvTbl["pvFname"]
        ]

        # If we're pickling, name the output files accordingly
        if config['processing']['picklePrimaryVariables']:
            pvTbl["pvPath"] = pvTbl["pvPath"] + ".pkl"
        
        #Prior to adding to the pvDict, check that we have unique keys
        if any(pvTbl['pvPath'].isin(pvDict.keys())):
            sys.exit("Duplicate keys found in generating primary variables.")

        #Finally, make the dict
        pvDict[thisKey] =(
            pvTbl.groupby("pvPath")
            .apply(lambda x: list(x["inPath"]), include_groups=False)
            .to_dict()
        )

    # Secondary Variables---------------------------------------------
    # Setup the variable palette as a tabular list of files. As we add each
    # additional variable, we concatentate it onto the variable palette.
    varPal = pd.DataFrame([k for v in pvDict.values() for k in v.keys()], 
                          columns=["path"])
    varPal["fname"] = [os.path.basename(p) for p in varPal["path"]]
    varPal["varID"] = varPal["fname"].str.extract("^([^_]+)_.*$")
    varPal["srcID"] = varPal["fname"].str.extract("^[^_]+_([^_]+)_.*$")
    varPal["stems"] = varPal["fname"].str.extract("^[^_]+_[^_]+_(.+)$")
    svDict = {}
    # Iterate over secondary variables if they are request
    if "secondaryVars" in config:
        sys.exit("Not tested. TODO")
        for thisSV in config["secondaryVars"].values():
            # Convert varList into a workable format
            varTbl = filelistToDataframe(varList)
            # Now filter by the input variables needed for this derived variable
            selThese = [v in thisSV["inputVars"] for v in varTbl["varName"]]
            longSVTbl = varTbl[selThese]
            try:
                if longSVTbl.size == 0:
                    raise ValueError(
                        f"Cannot find any matching input files for {thisSV['name']}. "
                        + "Check the definition again. Also check the order of definition."
                    )
            except ValueError as e:
                print("Error:", e)

            # Pivot and retain only those in common
            svTbl = longSVTbl.pivot(
                index=["src", "stems"], columns="varName", values="path"
            )
            svTbl = svTbl.dropna().reset_index()
            # Now we have a list of valid files that can be made. Store the results
            validPaths = [
                os.path.join(outDirs["variables"], var, fName)
                for var in thisSV["outputVars"]
                for fName in f"{var}_" + svTbl["src"] + "_" + svTbl["stems"] + ".nc"
            ]

            svDict[thisSV["id"]] = thisSV
            svDict[thisSV["id"]]["files"] = validPaths
            varList += validPaths

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
                         thisInd["id"],
                         rw["indFname"])
            for idx, rw in varPal.iterrows()
        ]
        #Only extract the dict for the part that we are actually
        #interested in
        useThese = varPal["varID"] == thisInd["variables"]
        indDict[indKey] = {rw["indPath"]: [rw["path"]] \
                                    for idx, rw in varPal[useThese].iterrows()}

    # Regridding-----------------------------------------------------------------------
    # We only regrid if it is requested in the configuration
    doRegridding = config["outputGrid"]["regriddingEngine"] != "None"
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
            [i for this in indDict.values() for i in this["files"]], columns=["srcPath"]
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
    asInps = list(ensDict.keys())
    if config["arealstats"]["calcForMembers"]:
        asInps += [y for x in ensDict.values() for y in x]
    asTbl = pd.DataFrame(asInps, columns=["srcPath"])
    # Now setup output structures
    asTbl["srcFname"] = [os.path.basename(p) for p in asTbl["srcPath"]]
    asTbl["asFname"] = asTbl["srcFname"].str.replace("nc", "csv")
    asTbl["asPath"] = [os.path.join(outDirs["arealstats"], f) for f in asTbl["asFname"]]
    # Make the dict
    asDict = (
        asTbl.groupby("asPath")
        .apply(lambda x: list(x["srcPath"]), include_groups=False)
        .to_dict()
    )

    # Plots----------------------------------------------------
    # Collate and process sources for plots
    def makeInputDict(d):
        inpTbl = pd.DataFrame(list(d.keys()), columns=["path"])
        inpTbl["fname"] = [os.path.basename(f) for f in inpTbl["path"]]
        inpTbl["indId"] = inpTbl["fname"].str.extract("^(.*?)_.*$")
        inpTbl["indSrc"] = inpTbl["fname"].str.extract("^.*?_(.*?)_.*$")
        inpDict = (
            inpTbl.groupby("indId")
            .apply(lambda x: list(x["path"]), include_groups=False)
            .to_dict()
        )
        return inpDict

    asList = makeInputDict(asDict)
    ensList = makeInputDict(ensDict)

    # Loop over available indicators to make plots
    pltDict = {}
    for thisInd in config["indicators"].values():
        # But what should we plot? It depends on the nature of the indicator
        # * Period-based indicators should plot the spatial map and the plots
        # * Yearly (or monthly) based indicators show a time series
        if thisInd["time_binning"] == "periods":
            # Box plot
            bxpFname = os.path.join(outDirs["plots"], f"{thisInd['id']}_boxplot.png")
            pltDict[bxpFname] = asList[str(thisInd["id"])]

            # Spatial plot
            spFname = os.path.join(outDirs["plots"], f"{thisInd['id']}_spatial.png")
            pltDict[spFname] = ensList[str(thisInd["id"])]

        elif thisInd["time_binning"] in ["years", "months"]:
            # Time series plot
            lpFname = os.path.join(outDirs["plots"], f"{thisInd['id']}_lineplot.png")
            pltDict[lpFname] = asList[str(thisInd["id"])]

    # Collate and round off----------------------------------------------
    rtn = {
        "primVars": pvDict,
        "secondaryVars": svDict,
        "indicators": indDict,
        "regridded": rgDict,
        "ensstats": ensDict,
        "arealstats": asDict,
        "plots": pltDict,
    }
    # Create an "all" dict  containing 
    # all targets in the workflow
    allList = []
    for k, v in rtn.items():
        if k in ["primVars",
                 "indicators"]:  # Requires special handling, as these are nested lists
            for x in v.values():
                allList += x.keys()
        elif k in ["secondaryVars"]:  # Requires special handling, as these are nested lists
            for x in v.values():
                allList += x["files"]
        else:
            allList += v.keys()
    rtn["all"] = allList

    # Fin-----------------------------------
    return rtn
