import os
import pandas as pd
import glob
from pathlib import Path

"""
#Setup for debugging
pd.set_option('display.max_colwidth', None)
print(os.getcwd())
import workflow.KAPy as KAPy
config=KAPy.getConfig("./workflow/testing/config.yaml")
config=KAPy.getConfig("./config/config.yaml")
"""

def getWorkflow(config):
    """
    Get Workflow setup

    Generates a description of the workflow dependencies of this configuration
    """
    # Extract specific configurations
    outDirs = config["dirs"]

    # Primary Variables ---------------------------------------------------------------
    # PVs are the raw inputs. These need to be read into a single-file format based on
    # xarray, and are then exported as netcdf.
    # We loop over the individual items maintaining the dict format, as this is a touch easier to
    # work with
    pvDict = {}
    for thisKey, thisInp in config["inputs"].items():
        # Get file extension corresponding to rechunk strategy
        fileExtn={"none": "pkl",
                 "nc":"nc"}[thisInp['rechunkingStrategy']]

        # Input files can be specified in four different ways
        # We handle all of these cases to extract a list of files that we want.

        # Case 1. Glob - a glob is characterised by the presence of certain symbols in the string
        if any(c in thisInp['path'] for c in "*?[]" ):
            filelist=sorted(glob.glob(thisInp["path"]))
        # Then we we are dealing with a single file. First check that it exists
        else:
            input_path=Path(thisInp['path'])
            if not input_path.exists():
                raise FileNotFoundError(f"Cannot find input file '{input_path}'")
            # Case 2. Direct reference to a single NetCDF - we detect this and
            # can use it directly
            if  b"\x00" in open(thisInp['path'], "rb").read(1024):
                filelist=[input_path]
            # Assert that file must therefore be a text file
            # Case 3. Direct reference to an .md5 file, in the form of output from md5sum,
            # where the file path is in the second column
            elif input_path.suffix.lower() in [".md5"]:
                filelist=pd.read_csv(input_path,names=["md5","path"],
                                       header=None,
                                       sep=r"\s+",
                                       index_col=None)
                filelist=filelist["path"].tolist()
            #Case 4. Just read the file line-by-line
            else:
                with open(input_path) as f:
                    filelist=f.read().splitlines()

        #Handle case where we don't find any files. We could ignore it,
        # but it's best to throw an error
        if len(filelist)==0:
            raise FileNotFoundError(f'No files found for input path "{thisInp["path"]}"')

        # Setup import table and check that all of the files actually exist. This is not so important for a single NetCDF
        #but essential when we are supplying the filelist
        inpTbl = pd.DataFrame(filelist, columns=["inPath"])
        inpTbl['inFname']=[os.path.basename(p) for p in inpTbl['inPath']]
        inpTbl['exists']=[os.path.exists(f) for f in filelist]
        if not all(inpTbl['exists']):
            missing=inpTbl[~inpTbl['exists']]
            msg = (
                f"{len(missing)} required files are missing:\n"
                + "\n".join(f"  - {f}" for f in missing['inPath'])
            )            
            raise FileNotFoundError(msg)

        # If we only get one file, then there's not really much to do - that file
        # is the only member of the ensemble and we use it more or less directly
        # Handle that case first.
        elif len(inpTbl)==1:
            #Set output filename, setting the file extension manually.
            pvTbl=inpTbl
            pvTbl['pvFname']= \
                    f"{thisInp['datasetCode']}_{thisInp['varCode']}_{thisInp['gridCode']}_noexp_noensid.{fileExtn}"

        # A similar case also exists where there is a single ensemble member, but it
        # is spread across multiple files. This is indicated when the ensMemberFields and 
        # experimentField is empty. We handle all variates of that here
        elif thisInp['ensMemberFields']==[''] and thisInp['experimentField']=='' and len(inpTbl)>1:
            pvTbl=inpTbl
            pvTbl['pvFname']= \
        # elif thisInp['ensMemberFields']==['']:
        #     raise ValueError("Unhandled case. Please file a bug")
        # elif thisInp['experimentField']==['']:
        #     raise ValueError("Unhandled case. Please file a bug")
                    f"{thisInp['datasetCode']}_{thisInp['varCode']}_{thisInp['gridCode']}_noexp_noensid.{fileExtn}"
        # Else multiple hits detected that need to be handled.
        else:
            # Handling multiple files requires some information from the filenames, 
            # and therefore the fieldSeparator needs to be defined. If not, throw an error
            if thisInp['fieldSeparator']=='':
                raise ValueError(f'fieldSeparator is not defined for input ID "{thisInp['id']}" ' + \
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
                    f"{thisInp['datasetCode']}_{thisInp['varCode']}_{thisInp['gridCode']}_" + \
                    inpTbl['experiment'] + "_" + \
                    inpTbl['ensMemberID'] +"." + fileExtn

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
                        f"{thisInp['datasetCode']}_{thisInp['varCode']}_{thisInp['gridCode']}" + \
                        f"_{thisInp["commonExperiment"]}+{thisExpt}_" + \
                        theseExptFiles['ensMemberID'] +"." + fileExtn
                    commonExptTable['pvFname']= \
                        f"{thisInp['datasetCode']}_{thisInp['varCode']}_{thisInp['gridCode']}" + \
                        f"_{thisInp["commonExperiment"]}+{thisExpt}_" + \
                        commonExptTable['ensMemberID'] +"."+fileExtn
                    
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
        pvTbl["pvLeaf"] = [
            os.path.join(thisInp['datasetCode'], thisInp['varCode'],f)
            for f in pvTbl["pvFname"]
        ]

        #Prior to adding to the pvDict, check that we have unique keys
        if any(pvTbl['pvLeaf'].isin(pvDict.keys())):
            raise ValueError("Duplicate keys found in generating primary variables.")

        #Finally, group the inputfiles together and copy into pvDict
        grouped_inputs =(
            pvTbl.groupby("pvLeaf")
            .apply(lambda x: list(x["inPath"]), include_groups=False)
            .to_dict()
        )
        for outLeaf in grouped_inputs.keys():
            pvDict[outLeaf] = {
                "groupID": thisKey,
                "inputs": grouped_inputs[outLeaf],
                "outputs": os.path.join(outDirs["primaryVariables"],outLeaf)
            }


    # # Secondary Variables---------------------------------------------
    # # Setup the variable palette as a tabular list of files. As we add each
    # # additional variable, we concatentate it onto the variable palette.
    def parseFilelist(flist,src):
        thisTbl = pd.DataFrame(flist,columns=["path"])
        thisTbl["fname"] = [os.path.basename(p) for p in thisTbl["path"]]
        thisTbl["src"] = src
        thisTbl["dataset"] = thisTbl["fname"].str.extract("^([^_]+)_.*$")
        thisTbl["var"] = thisTbl["fname"].str.extract("^[^_]+_([^_]+)_.*$")
        thisTbl["grid"] = thisTbl["fname"].str.extract("^[^_]+_[^_]+_([^_]+)_.*$")
        thisTbl["expt"] = thisTbl["fname"].str.extract("^[^_]+_[^_]+_[^_]+_([^_.]+).*$")
        thisTbl["stem"] = thisTbl["fname"].str.extract("^[^_]+_[^_]+_[^_]+_[^_]+_(.+).(?:nc|pkl)$")
        return thisTbl

    varPal = parseFilelist([v["outputs"] for v in pvDict.values()],
                           "primaryVariables")

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
                index=["dataset","grid","expt", "stem"], columns="var", values="path"
            )
            svTbl = svTbl.dropna().reset_index()
            if svTbl.size == 0:
                raise ValueError(f"Cannot find any matching input variables for {thisSV['id']}. ")

            # Now we have a list of valid dataset/grid/expt/stem combinations that are valid and 
            # have the required input variables. For each of these combinations, we then want to produce
            # the output files, which we store in svDict
            svTbl["id"]= svTbl['dataset']+"_"+svTbl['grid']+"_"+svTbl["expt"]+"_"+svTbl["stem"]

            #Setup dict
            inp_dict =svTbl.set_index("id")[thisSV['inputVars']].to_dict(orient="index")
            out_rule= {v: os.path.join(outDirs['secondaryVariables'],
                                        "{dataset}",
                                        v,
                                        f"{{dataset}}_{v}_{{leaf}}.nc") 
                        for v in thisSV['outputVars']
                        }
            this_SV_dict={"input_dict": inp_dict,
                        "output_rule":out_rule,
                        "outputs": []}
            for idx, rw in svTbl.iterrows():
                for this_var in thisSV['outputVars']:
                    output_file= rw["dataset"] +f"_{this_var}_" + rw['grid']+"_"+rw["expt"]+"_"+rw["stem"]+".nc"
                    this_SV_dict['outputs'] += [os.path.join(outDirs["secondaryVariables"], 
                                                                rw["dataset"],
                                                                this_var,
                                                                output_file)]

            # Add to output dict
            svDict[thisSV['id']] = this_SV_dict

            # Add to variable palette
            varPal = pd.concat([varPal,
                                parseFilelist(this_SV_dict['outputs'],"secondaryVariables")])

     # Bias Adjustment -------------------------------------------------------
    # Bias adjusted variables and secondary variables share a very similar logic
    # They only kick in if requested, draw upon the variable palette, and feed back
    # into when complete
    # The logic required though is more complex, as the input variable can be sourced from
    # multiple locations (primary or secondary) and the grids can differ wildly. However,
    # the transformation is a 1(+1):1, i.e. histsim (+ref) : output, so that makes it well suited
    # to use a dictionary lookup. Don't ask me what we do when we get to multi-dimension bias-correction
    BADict = {}
    if "biasAdjustment" in config:
        for thisKey,thisBA in config["biasAdjustment"].items():
            # Firstly, identify the reference dataset. Note that there should only be one reference
            # file for each case
            selThese = (varPal["var"] ==thisBA['baVariable']) & \
                        (varPal["dataset"]==thisBA['refDataset'])
            if sum(selThese)!=1:
                raise ValueError("Cannot find a unique data variable to use as the reference "
                                 + f'for bias adjustment of "{thisBA['baVariable']}_{thisBA['targetDataset']}"')
            refDict = varPal[selThese].to_dict(orient="records")[0]

            # Now identify the input files needed for this bias adjustment 
            selThese = (varPal["var"] ==thisBA['baVariable']) & \
                        (varPal["dataset"]==thisBA['targetDataset'])
            BAtbl = varPal[selThese].copy()
            try:
                if BAtbl.size == 0:
                    raise ValueError(
                        f"Cannot find any matching input files for {thisBA['id']}. "
                        + "Check the definition again. Also check the order of definition, as KAPy processes definitions sequentially."
                    )
            except ValueError as e:
                print("Error:", e)
            
            # The output grid is configurable and plays into the file name
            if thisBA['outputGrid']=="reference":
                BAtbl['outfile'] =f"{thisBA["outDatasetCode"]}_{thisBA["baVariable"]}_{refDict['grid']}_"+BAtbl["expt"]+"_"+BAtbl["stem"]+".nc"
            elif thisBA['outputGrid']=="target":
                BAtbl['outfile'] =f"{thisBA["outDatasetCode"]}_{thisBA["baVariable"]}_"+BAtbl['grid']+"_"+BAtbl["expt"]+"_"+BAtbl["stem"]+".nc"
            else:
                raise ValueError(f"Unknown output grid option, '{thisBA['outputGrid']}' supplied in bias adjustment row: '{thisKey}' ")

            # We've therefore identified what needs to be done. Here we follow the approach
            # used above for building up lookup dicts, even though its not strictly needed
            # as bias-adjustment is a 1(+1):1 mapping. 
            # The lookup id is also only based on the experiment and the stem, as everything else is determined
            # by the groupID - in particular the change of grid upon bias-adjustment causes issues with 
            # file naming. There is potential for problems here that we need to live with. 
            BAtbl['id'] =BAtbl["expt"]+"_"+BAtbl["stem"]
            #Just use the output filename instead as id...
            BAtbl['id']= BAtbl['outfile']

            #Setup dict
            inp_dict={}
            for idx,rw in BAtbl.iterrows():
                inp_dict[rw['id']] = {'target':rw['path'],
                                      "ref": refDict['path']}
            out_rule= {thisBA['baVariable']: os.path.join(outDirs['biasAdjustment'],
                                        thisBA["outDatasetCode"],
                                        thisBA['baVariable'],
                                        f"{{leaf}}") 
                                        #f"{thisBA["outDatasetCode"]}_{thisBA['baVariable']}_{{leaf}}.nc") 
                        }
            this_BA_dict={"input_dict": inp_dict,
                        "output_rule":out_rule,
                        "outputs": [os.path.join(outDirs["biasAdjustment"],
                                                 thisBA["outDatasetCode"],
                                                 thisBA["baVariable"],
                                                 this_out_file)
                                    for this_out_file in BAtbl['outfile']]  }
            BADict[thisKey]=this_BA_dict

        #Add to variable palette. Note that we add the bias-adjusted variables here as one large chunk
        #rather than incrementally as is done for derived variables, as we don't want to bias adjust
        #bias-adjusted variables.
        BA_outputs=[f for v in BADict.values() for f in v["outputs"] ]
        varPal = pd.concat([varPal,
                            parseFilelist( BA_outputs,"biasAdjustment")])

    # Tertiary Variables---------------------------------------------
    # Iterate over tertiary variables if they are requested. The approach
    # here is very similar to secondary variables, but we only draw on
    # the variables from bias adjustment palette  and any others that are created previosuly 
    # (i.e. the postBAPal) instead of the full variable palette.
    # Note that tertiary variables can only be created if there are bias adjusted variables 
    # created first
    tvDict = {}
    if ("tertiaryVars" in config) and ("biasAdjustment" in config):
        postBAPal = parseFilelist(BA_outputs,"biasAdjustment")
        for thisKey,thisTV in config["tertiaryVars"].items():

            # Filter by the input variables needed for this derived variable
            selThese = [v in thisTV["inputVars"] for v in postBAPal["var"]]
            longTVTbl = postBAPal[selThese]
            if longTVTbl.size == 0:
                    raise ValueError(f"Cannot find any input variables for tertiary variable '{thisTV['id']}'. ")

            # Pivot and retain only those in common
            tvTbl = longTVTbl.pivot(
                index=["dataset","grid","expt", "stem"], columns="var", values="path"
            )
            tvTbl = tvTbl.dropna().reset_index()
            if tvTbl.size == 0:
                raise ValueError(f"Cannot find matching input variables for tertiary variable '{thisTV['id']}'. ")

            # Now we have a list of valid dataset/grid/expt/stem combinations that are valid and 
            # have the required input variables. For each of these combinations, we then want to produce
            # the output files, which we store in svDict
            tvTbl["id"]= tvTbl['dataset']+"_"+tvTbl['grid']+"_"+tvTbl["expt"]+"_"+tvTbl["stem"]

            #Setup dict
            inp_dict =tvTbl.set_index("id")[thisTV['inputVars']].to_dict(orient="index")
            out_rule= {v: os.path.join(outDirs['tertiaryVariables'],
                                        "{dataset}",
                                        v,
                                        f"{{dataset}}_{v}_{{leaf}}.nc") 
                        for v in thisTV['outputVars']
                        }
            this_TV_dict={"input_dict": inp_dict,
                        "output_rule":out_rule,
                        "outputs": []}
            for idx, rw in tvTbl.iterrows():
                for output_var in thisTV['outputVars']:
                    output_file= rw["dataset"] +f"_{output_var}_" + rw['grid']+"_"+rw["expt"]+"_"+rw["stem"]+".nc"
                    this_TV_dict['outputs'] +=[os.path.join(outDirs["tertiaryVariables"], 
                                                          rw["dataset"],
                                                          output_var,
                                                          output_file)]

            # Add to output dict
            tvDict[thisTV['id']] = this_TV_dict

            # Add to variable palette
            varPal = pd.concat([varPal,
                                parseFilelist(this_TV_dict['outputs'],"tertiaryVariables")])
            postBAPal=pd.concat([postBAPal,
                                parseFilelist(this_TV_dict['outputs'],"tartiaryVariables")])


    # Indicators -----------------------------------------------------
    # Loop over indicators and get required files
    # The approach used here is based on a look-up dictionary approach,
    # but the number of outputs can vary across indicators. We therefore define
    # the output rule, together with the groupID, output list and input dict
    indDict = {}
    for indKey, thisInd in config["indicators"].items():
        # Find the right files to consider first
        varPal['correctVar'] = [v in thisInd["variables"] for v in varPal["var"]]
        varPal['correctDataset']=[v in thisInd['datasets']  for v in varPal['dataset']]
        if "all" in thisInd['datasets']:
            useThese = varPal['correctVar']
        else:
            useThese = varPal['correctVar'] & varPal['correctDataset']
        if not any(useThese):
            raise ValueError(f"Cannot find variable(s) '{thisInd["variables"]}' for datasets '{thisInd['datasets']}' to calculate indicators from.")
        long_ind_tbl=varPal[useThese].copy()

        # Pivot and retain only those in common
        wide_ind_tbl = long_ind_tbl.pivot(
            index=["dataset","grid","expt", "stem"], columns="var", values="path"
        )
        wide_ind_tbl = wide_ind_tbl.dropna().reset_index()
        if wide_ind_tbl.size == 0:
            raise ValueError(f"Cannot find any matching input variables for indicator id '{thisInd['id']}'. ")

        # Now we have a list of valid dataset/grid/expt/stem combinations that are valid and 
        # have the required input variables. This combination is used to form a unique id
        # that can be extracted from the output file, and also used as the lookup key.
        wide_ind_tbl["id"]= wide_ind_tbl['dataset']+"_"+wide_ind_tbl['grid']+"_"+wide_ind_tbl["expt"]+"_"+wide_ind_tbl["stem"]

        #Setup dict
        inp_dict =wide_ind_tbl.set_index("id")[thisInd['variables']].to_dict(orient="index")
        out_rule= {v: os.path.join(outDirs['indicators'],
                                    "{dataset}",
                                    v,
                                    f"{{dataset}}_{v}_{{leaf}}.nc") 
                    for v in thisInd['indicator_codes']
                    }
        this_ind_dict={"input_dict": inp_dict,
                       "output_rule":out_rule,
                       "outputs": []}
        for idx, rw in wide_ind_tbl.iterrows():
            for ind_id in thisInd['indicator_codes']:
                output_file= rw["dataset"] +f"_{ind_id}_" + rw['grid']+"_"+rw["expt"]+"_"+rw["stem"]+".nc"
                this_ind_dict['outputs'] += [os.path.join(outDirs["indicators"], 
                                                            rw["dataset"],
                                                            ind_id,
                                                            output_file)]

        # Add to output dict
        indDict[indKey] = this_ind_dict

    # Regridding-----------------------------------------------------------------------
    # We only regrid if it is requested in the configuration
    doRegridding = config["outputGrid"]["templateType"] != "none"
    if doRegridding:
        # Remap directory
        rgTbl = pd.DataFrame([i for v in indDict.values() for i in v['outputs']], 
                          columns=["input_path"])
        rgTbl["input_dir"] = [os.path.dirname(f) for f in rgTbl["input_path"]]
        rgTbl["input_fname"] = [os.path.basename(p) for p in rgTbl["input_path"]]
        #Update filenames and directories, replacing thegrid code in the filename 
        # and the output path
        rgTbl['output_dir'] = \
            rgTbl["input_dir"].str.replace(outDirs['indicators'],
                                           outDirs['regridded'],
                                           regex=False)
        rgTbl['output_fname'] = \
            rgTbl["input_fname"].str.replace(r'^([^_]+_[^_]+_)[^_]+(_.*$)',
                                        r'\1'+config['outputGrid']['gridName']+r'\2',
                                        regex=True)
        #Build the rest of the paths
        rgTbl["output_path"] = [
            os.path.join(rw["output_dir"], rw["output_fname"])
            for idx, rw in rgTbl.iterrows()
        ]

        #Check for the presence of duplicates in output_path. Fail if found
        if len(rgTbl['output_path'].unique()) != len(rgTbl):
            duplicates = rgTbl['output_path'][rgTbl['output_path'].duplicated()].unique()
            msg = (
                f"{len(duplicates )} duplicated filenames arise in regridding step. Please recheck configuration:\n"
                + "\n".join(f"  - {f}" for f in duplicates)
            )            
            raise ValueError(msg)
        
        # Create the dict
        inp_dict=rgTbl.set_index('output_path')[['input_path']].to_dict(orient="index")
        rgDict = {"input_dict":inp_dict,
                  "outputs": rgTbl['output_path'].tolist()}
    else:
        rgDict = {}

    # Ensembles----------------------------------------------------------------------------
    # Build ensemble membership - the exact source here depends on whether
    # we are doing regridding or not
    if doRegridding:
        ensTbl = pd.DataFrame(rgDict["outputs"], columns=["source_path"])
    else:
        ensTbl = pd.DataFrame(
            [k for v in indDict.values() for k in v['outputs']], columns=["source_path"]
        )
    ensTbl["source_fname"] = [os.path.basename(p) for p in ensTbl["source_path"]]
    ensTbl["ensemble_id"] = ensTbl["source_fname"].str.extract("^([^_]+_[^_]+_[^_]+_[^_]+)_.*$")
    ensTbl["ensemble_path"] = [
        os.path.join(outDirs["ensstats"], f + "_ensstats.nc") for f in ensTbl["ensemble_id"]
    ]

    #Setup dict
    inp_dict = (
        ensTbl.groupby("ensemble_path")
        .apply(lambda x: list(x["source_path"]), include_groups=False)
        .to_dict()
    )
    ensDict={"input_dict":inp_dict,
             "outputs": list(inp_dict.keys())}

    # Arealstatistics----------------------------------------------
    # Start by building list of input files to calculate arealstatistics for
    # Note that we split into ensemble and member statistics
    ensemble_inputs = pd.DataFrame(ensDict['outputs'],columns=['source_path'])
    ensemble_inputs['type']='ensstats'
    member_inputs = pd.DataFrame([y for x in ensDict["input_dict"].values() for y in x],
                             columns=['source_path'])
    member_inputs['type']='members'
    asTbl=pd.concat([ensemble_inputs,member_inputs])
    # Now setup output structures
    asTbl["source_fname"] = [os.path.basename(p) for p in asTbl["source_path"]]
    asTbl["as_fname"] = asTbl["source_fname"].str.replace("nc", "csv",regex=False)
    asTbl["as_path"] = [os.path.join(outDirs["arealstats"], rw["type"], rw["as_fname"]) \
                       for idx, rw in asTbl.iterrows()]
    # Make the dict
    inp_dict = (
        asTbl.groupby("as_path")
        .apply(lambda x: list(x["source_path"]), include_groups=False)
        .to_dict()
    )
    asDict={"input_dict":inp_dict,
            "outputs":list(inp_dict.keys())}

    #Separate the lists of area statistics into ensstats and members for use in
    #the database output
    mergedCSVDict= asTbl.groupby("type").apply(lambda x: list(x["as_path"]), include_groups=False).to_dict()

    # # Plots----------------------------------------------------
    # #Get list of areal statistics csv files (in the ensstats version)
    # csvTbl = pd.DataFrame(asDict['outputs'], columns=["path"])
    # csvTbl["fname"] = [os.path.basename(f) for f in csvTbl["path"]]
    # csvTbl["indicator_id"] = csvTbl["fname"].str.extract("^([^_]+)_.*$")
    # csvTbl["member_id"] = csvTbl["fname"].str.extract("^[^_]+_[^_]+_[^_]+_[^_]+_(.+).*$")
    # csvTbl=csvTbl[csvTbl["member_id"]=='ensstats.csv']
    # csvDict = (
    #     csvTbl.groupby("indicator_id")
    #     .apply(lambda x: list(x["path"]), include_groups=False)
    #     .to_dict()
    # )
    
    # #And of the netcdf files
    # ncList = pd.DataFrame(list(ensDict.keys()), columns=["path"])
    # ncList["fname"] = [os.path.basename(f) for f in ncList["path"]]
    # ncList["indId"] = ncList["fname"].str.extract("^([^_]+)_.*$")
    # ncDict = (
    #     ncList.groupby("indId")
    #     .apply(lambda x: list(x["path"]), include_groups=False)
    #     .to_dict()
    # )

    # # Loop over available indicators to make plots
    # pltDict = {}
    # for thisInd in config["indicators"].values():
    #     # But what should we plot? It depends on the nature of the indicator
    #     # * Period-based indicators should plot the spatial map and the plots, derived
    #     #   from the ensemble statistics
    #     # * Yearly (or monthly) based indicators show a time series, also for ensemble statistcs
    #     if thisInd["timeBinning"] == "periods":
    #         # Box plot - requires ensemble csv files
    #         bxpFname = os.path.join(outDirs["outputs"],'plots', f"{thisInd['id']}_boxplot.png")
    #         pltDict[bxpFname] = csvDict[str(thisInd["id"])]

    #         # Spatial plot - requires ensemble netcdf files
    #         spFname = os.path.join(outDirs["outputs"],'plots', f"{thisInd['id']}_spatial.png")
    #         pltDict[spFname] = ncDict[str(thisInd["id"])]

    #     elif thisInd["timeBinning"] in ["years", "months"]:
    #         # Time series plot - requires ensemble csv files
    #         lpFname = os.path.join(outDirs["outputs"],'plots', f"{thisInd['id']}_lineplot.png")
    #         pltDict[lpFname] = csvDict[str(thisInd["id"])]

    # Collate and round off----------------------------------------------
    rtn = {
        "primary_vars": pvDict,
        "secondary_vars": svDict,
        "bias_adj":BADict,
        "tertiary_vars": tvDict,
        "indicators": indDict,
        "regrid": rgDict,
        "ensstats": ensDict,
        "arealstats": asDict,
        "mergedCSVs":mergedCSVDict}
    #     "plots": pltDict,
    # }

    # Create an "all" dict  containing 
    # all targets in the workflow
    allList = []
    for k, v in rtn.items():
        if k in ["primary_vars"]:  # Skip this
            allList += [v["outputs"] for v in pvDict.values()]
        elif k in ["secondary_vars",
                 "bias_adj",
                 "tertiary_vars",
                 "indicators"]:  # Requires special handling, as these are nested lists
            for x in v.values():
                allList += x["outputs"]
        elif k in ["mergedCSVs"]:  # Skip this
            continue
        elif k in ["regrid"]:  # Skip if we're not regridding
            if doRegridding:
                allList += v["outputs"]
        else:
            allList += v["outputs"]
    rtn["all"] = allList

    # Fin-----------------------------------
    return rtn



