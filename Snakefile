#Klimaatlas Ghana Snakemake configuration file

import KAPy
import os
import re
import glob

#Load configuration 
config=KAPy.loadConfig()  

# Downloading ------------------------
rule URLs:
    run:
        KAPy.searchESGF(config)

rule downloads:
    input: 
        expand(os.path.join(KAPy.getFullPath(config,'modelInputs'),'{fname}'),
               fname=[re.sub('.url','',x) 
                      for x in os.listdir(KAPy.getFullPath(config,'URLs'))])
        
rule download:
    output:
        os.path.join(KAPy.getFullPath(config,'modelInputs'),'{fname}.nc')
    input: 
        #Only download if a new URL has been added - ignore updates
        ancient(os.path.join(KAPy.getFullPath(config,'URLs'),'{fname}.nc.url'))
    run:
        KAPy.downloadESGF(config,input,output)

# Collate---------------------------------
# Compile the data available into xarray datasets for further processing
# TODO: Establish dependencies here
rule xarrays:
    run:
        KAPy.makeDatasets(config)
        
# Derived indicators -------------------------
#A useful concept is also the idea of "derived variables", that we might need to calculate as
#intermediate steps in the processing chain, before we calculate indicators from them.
#Good examples include FWI and PoteEvap
#Remember that they will also need xarray pickles too

# Bias correction -------------------
# TODO

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
            KAPy.calculateStatistics(indicator=thisInd,
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

# Enssemble Statistics ---------------------------------
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



scenarioList=[sc['name'] for sc in config['scenarios'].values()]
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
