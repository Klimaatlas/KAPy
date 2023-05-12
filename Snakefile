#Snakemake configuration file

import KAPy
import os

#Load a configuration
cfg=KAPy.configs.loadConfig('configs/Ghana','config')
esgf=KAPy.configs.loadConfig('configs/Ghana','ESGF')

fnames= os.listdir(os.path.join('scratch','downloads','URLs'))

configfile: "config.yaml"

rule all:
    input: 
        expand(os.path.join('scratch','downloads','data','{fname}'),
               fname=fnames)
        
rule download:
    input:
        os.path.join('scratch','downloads','URLs','{fname}.nc')
    output:
        os.path.join('scratch','downloads','data','{fname}.nc')
    run:
        KAPy.download.ESGF(input[0],cfg,esgf)
        

rule DMI:
    input:
        'scratch/downloads/data/tas_AFR-44_ECMWF-ERAINT_evaluation_r1i1p1_DMI-HIRHAM5_v2_mon_198901-199012.nc'
        

