"""
#Setup for debugging with a Jupyterlab console
import os
os.chdir("..")
import KAPy
os.chdir("..")
config=KAPy.getConfig("./config/config.yaml")  
inFile=["results/2.indicators/101/101_CORDEX_rcp85_AFR-22_MPI-M-MPI-ESM-LR_r1i1p1_GERICS-REMO2015_v1_mon.nc"]
inFile=["resources/CORDEX/tas_AFR-22_MPI-M-MPI-ESM-LR_rcp85_r1i1p1_GERICS-REMO2015_v1_mon_200601-201012.nc"]
outFile=["results/3.common_grid/101/101_CORDEX_rcp85_AFR-22_MPI-M-MPI-ESM-LR_r1i1p1_GERICS-REMO2015_v1_mon.nc"]
"""

from cdo import Cdo
import sys
    
def regrid(config,inFile,outFile):
    #Currently only works for 'cdo' regridding. Other engines such as xesmf could be supported in the future
    if not config['outputGrid']['regriddingEngine']=='cdo':
        sys.exit("Regridding options are currently limited to cdo. See documentation")
        
    #Setup CDO object
    cdo=Cdo()

    #Apply regridding
    cdo.remapbil(config['outputGrid']['cdoGriddes'],
                 input=inFile[0],
                 output=outFile[0])
