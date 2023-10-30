# KAPy Workflow
#
# This snakemake workflow handles the downloading and processing of data for use
# in Klimaatlas-like products. 
#
# The pipeline can be run using
#    > snakemake --cores 1 <target>
#
# A list of available target rules can be obatined using
#   > snakemake -S
#
# Workflow configuration options are set in config.yaml
#

import KAPy
import os
import re
import glob

#Configuratioon -----------------------
#Load configuration 
config=KAPy.loadConfig()  

#Setup directories
rule setup:
    run:
        for d in config['dirs'].keys():
            thisDir=KAPy.buildPath(config,d)
            if not os.path.exists(thisDir):
                os.mkdir(thisDir)

# Downloading ------------------------
# This part of the script is activated by the "download" key in
# the config file. If no download parameters decleared, then don't activate the rules
# Instead, the script will work with files from disk
if config['download']:
    rule search:
        run:
            KAPy.searchESGF(config)
            
    #Load ESGF configuration for use here
    ESGFcfg=KAPy.loadConfig(config['download']['ESGF'],useDefaults=False)
    rule URLs: #Create flag files to show script ran ok
        input:
            expand(KAPy.buildPath(config,'search','{varname}.ok'),
                   varname=ESGFcfg['variables'].keys())
            

    def varRule(varname):
        rule:
            name: f'URLs_{varname}'
            output:
                touch(KAPy.buildPath(config,'search',f'{varname}.ok'))
            input:
                KAPy.buildPath(config,'search',f'{varname}.pkl')
            run:
                KAPy.getESGFurls(config,input)

    for thisVar in ESGFcfg['variables'].keys():
        varRule(thisVar)

    rule download:
        input: 
            expand(KAPy.buildPath(config,'inputs','{fname}'),
                   fname=[re.sub('.url','',x) 
                          for x in os.listdir(KAPy.buildPath(config,'URLs'))])

    rule download_file:
        output:
            KAPy.buildPath(config,'inputs','{fname}.nc')
        input: 
            #Only download if a new URL has been added - ignore updates
            ancient(KAPy.buildPath(config,'URLs','{fname}.nc.url'))
        run:
            KAPy.downloadESGF(config,input,output)

    rule download_status:
        output:
            KAPy.buildPath(config,'notebooks','Download_status.nb.html')
        input: #Any changes in the two directories will trigger a rebuild
            KAPy.buildPath(config,'URLs'),
            KAPy.buildPath(config,'inputs')
        script:
            "./notebooks/Download_status.Rmd"

# Collate datasets---------------------------------
# Compile the data available into xarray dataset objects for further processing
# Get the full list of model inputs first
allInputs=glob.glob(KAPy.buildPath(config,'inputs',"*.nc"))

#Plural rule
rule datasets:
    input:
        [KAPy.buildPath(config,'datasets',f) \
                     for f in KAPy.inferDatasets(config,allInputs)]

#Singular rule
#Requires a bit of a hack with a lamba function to be able to both use a input function
#and feed additional arguments to the function
rule dataset_single:
    output:
        KAPy.buildPath(config,'datasets',"{stem}.nc.pkl")
    input:
        lambda wildcards: KAPy.deduceDatasetInputs(config,
                                                   wildcards.stem+".nc.pkl",
                                                   allInputs)
    run:
        KAPy.buildDataset(config,input,output)
    
        
# Bias correction -------------------
# TODO

# Derived variables -------------------------
#A useful concept is also the idea of "derived variables", that we might need to calculate as
#intermediate steps in the processing chain, before we calculate indicators from them.
#Good examples include FWI and PoteEvap
#Remember that they will also need xarray pickles too
#Can discuss whether we do this before or after bias correction
#TODO


# Indicators ---------------------------------
# Create a loop over the indicators that defines the singular and plural rules
# In particular,start with the assumption of univariate indicators - we can always extend it later. The trick will be to loop over the indicators indvidiually, rather than trying to 
#do it all in one hit.
allDatasets=glob.glob(KAPy.buildPath(config,'datasets',"*.nc.pkl"))

def ind_single_rule(thisInd):
    rule:  #Indicator singular rule
        name: f'i{thisInd["id"]}_file'
        output:
            KAPy.buildPath(config,'indicators',f'i{thisInd["id"]}_'+'{stem}')
        input:
            KAPy.buildPath(config,'datasets',f'{thisInd["variables"]}_'+'{stem}.pkl')
        run:
            KAPy.calculateIndicators(thisInd=thisInd,
                                     config=config,
                                     outPath=output,
                                     datPkl=input)
def ind_plural_rule(thisInd):
    rule:  #Indicator plural rule
        name: f'i{thisInd["id"]}'
        input:
            expand(KAPy.buildPath(config,'indicators','i{id}_{stem}.nc'),
                   id=thisInd['id'],
                   stem=[re.sub('^.+?_|.nc.pkl','',os.path.basename(x)) for x in allDatasets])
            
for thisInd in config['indicators'].values():
    ind_single_rule(thisInd)
    ind_plural_rule(thisInd)
    
           
# Regridding  ---------------------------------
# Combining everything into an ensemble requires that they are all on a common grid
# This is not always the case, and so we add a regridding step prior to ensemble calculation
rule regrid:
    input:
        expand(KAPy.buildPath(config,'gridded','{stem}.nc'),
               stem=glob_wildcards(KAPy.buildPath(config,'indicators','{stem}.nc')).stem)

rule regrid_file:
    output:
        KAPy.buildPath(config,'gridded','{stem}.nc')
    input:
        KAPy.buildPath(config,'indicators','{stem}.nc')
    run:
        KAPy.regrid(config,input,output)


# Enssemble Statistics ---------------------------------
# Now we can combine them
datasetList=[ds['shortname'] for ds in config['datasets'].values()]
indList=[ind['id'] for ind in config['indicators'].values()]
rule ensstats:
    input:
        expand(KAPy.buildPath(config,'ensstats','i{ind}_ensstat_{dataset}.nc'),
               ind=indList,
               dataset=datasetList)

def enstat_rule(ind,ds):
        rule:
            name: f'ensstat_i{ind}_{ds}'
            output:
                KAPy.buildPath(config,'ensstats',f'i{ind}_ensstat_{ds}.nc')
            input:
                glob.glob(KAPy.buildPath(config,'indicators',f'i{ind}_*_{ds}_*.nc'))
            run:
                KAPy.generateEnsstats(config,input,output)

for thisDS in datasetList:
    for thisInd in indList:
        enstat_rule(thisInd,thisDS)

# Outputs ---------------------------------
# Notebooks, amongst other things
rule notebooks:
    output:
        KAPy.buildPath(config,'notebooks','Indicator_notebook.nb.html')
    input: #Any changes in this directory will trigger a rebuild
        KAPy.buildPath(config,'ensstats')
    script:
        "./notebooks/Indicator_plots.Rmd"
        
