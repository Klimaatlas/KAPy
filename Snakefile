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
for d in config['dirs'].keys():
    thisDir=KAPy.getFullPath(config,d)
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

    rule download:
        input: 
            expand(os.path.join(KAPy.getFullPath(config,'modelInputs'),'{fname}'),
                   fname=[re.sub('.url','',x) 
                          for x in os.listdir(KAPy.getFullPath(config,'URLs'))])

    rule download_file:
        output:
            os.path.join(KAPy.getFullPath(config,'modelInputs'),'{fname}.nc')
        input: 
            #Only download if a new URL has been added - ignore updates
            ancient(os.path.join(KAPy.getFullPath(config,'URLs'),'{fname}.nc.url'))
        run:
            KAPy.downloadESGF(config,input,output)

    rule download_status:
        output:
            os.path.join(KAPy.getFullPath(config,'notebooks'),'Download_status.nb.html')
        input: #Any changes in the two directories will trigger a rebuild
            KAPy.getFullPath(config,'URLs'),
            KAPy.getFullPath(config,'modelInputs')
        script:
            "./notebooks/Download_status.Rmd"

# Collate---------------------------------
# Compile the data available into xarray datasets for further processing
# TODO: Establish dependencies here
rule xarrays:
    run:
        KAPy.makeDatasets(config)

        
# Bias correction -------------------
# TODO

# Derived indicators -------------------------
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

for thisInd in config['indicators'].values():
    rule:  #Indicator singular rule
        name: f'i{thisInd["id"]}_file'
        output:
            os.path.join(KAPy.getFullPath(config,'indicators'),
                         f'i{thisInd["id"]}_'+'{stem}.nc')
        input:
            os.path.join(KAPy.getFullPath(config,'xarrays'),
                                   f'{thisInd["variables"]}_'+'{stem}.pkl')
        run:
            KAPy.calculateIndicators(indicator=thisInd,
                                                config=config,
                                                outPath=output,
                                                datPkl=input)
    rule:  #Indicator plural rule
        name: f'i{thisInd["id"]}'
        input:
            expand(os.path.join(KAPy.getFullPath(config,'indicators'),
                            'i{id}_{stem}.nc'),
               id=thisInd['id'],
               stem=[re.sub('^.+?_|.pkl','',x) \
                     for x in os.listdir(KAPy.getFullPath(config,'xarrays'))])

# Regridding  ---------------------------------
# Combining everything into an ensemble requires that they are all on a common grid
# This is not always the case, and so we add a regridding step prior to ensemble calculation
rule regrid:
    input:
        expand(os.path.join(KAPy.getFullPath(config,'gridded'),'{stem}.nc'),
               stem=glob_wildcards(os.path.join(KAPy.getFullPath(config,'indicators'),
                                                '{stem}.nc')).stem)

rule regrid_file:
    output:
        os.path.join(KAPy.getFullPath(config,'gridded'),'{stem}.nc')
    input:
        os.path.join(KAPy.getFullPath(config,'indicators'),'{stem}.nc')
    run:
        KAPy.regrid(config,input,output)


# Enssemble Statistics ---------------------------------
# Now we can combine them
scenarioList=[sc['shortname'] for sc in config['scenarios'].values()]
indList=[ind['id'] for ind in config['indicators'].values()]
rule ensstats:
    input:
        expand(os.path.join(KAPy.getFullPath(config,'ensstats'),
                            'i{ind}_ensstat_{scenario}.nc'),
               ind=indList,
               scenario=scenarioList)

for sc in scenarioList:
    for ind in indList:
        rule:
            name: f'ensstat_i{ind}_{sc}'
            output:
                os.path.join(KAPy.getFullPath(config,'ensstats'),
                         f'i{ind}_ensstat_{sc}.nc')
            input:
                glob.glob(os.path.join(KAPy.getFullPath(config,'indicators'),
                                       f'i{ind}_*_{sc}_*.nc'))
            run:
                KAPy.generateEnsstats(config,input,output)
