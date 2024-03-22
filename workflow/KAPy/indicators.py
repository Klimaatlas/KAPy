"""
#Setup for debugging with a Jupyterlab console
import os
os.chdir("..")
import KAPy
os.chdir("..")
config=KAPy.loadConfig()  
inFile=['results/1.primVars/tas_CORDEX_rcp85_AFR-22_MPI-M-MPI-ESM-LRr1i1p1_GERICS-REMO2015_v1_mon.nc']
indID=101
"""

import pickle
import xarray as xr
import os
import numpy as np
import sys

def calculateIndicators(config,inFile,outFile,indID):
    
    #Retrieve indicator information
    thisInd=config['indicators'][indID]
    
    #Read the dataset object back from disk, depending on the configuration
    inExt=os.path.splitext(os.path.basename(inFile[0]))[1] 
    if inExt == '.nc':
        thisDat=xr.open_dataarray(inFile[0])
    elif inExt == '.pkl': #Read pickle
        with open(inFile[0],'rb') as f:
            thisDat=pickle.load(f)
    else:
        sys.exit(f'Unknown file format, {inExt} in {inFile[0]}')

    #Filter by season first (should always work)
    theseMonths=config['seasons'][thisInd['season']]['months']
    datSeason=thisDat.sel(time=np.isin(thisDat.time.dt.month,theseMonths))
        
    #Time binning over periods
    if thisInd['time_binning']=='periods':
        slices=[]
        periodIds=[]
        for thisPeriod in config['periods'].values():
                #Slice dataset
                timemin=datSeason.time.dt.year >=thisPeriod['start']
                timemax=datSeason.time.dt.year <=thisPeriod['end']
                datPeriodSeason=datSeason.sel(time=timemin & timemax)
                #If there is nothing left, we want a result all the same so that we
                #can put it in the outputs
                if datPeriodSeason.time.size==0:
                    res=datPeriodSeason.drop_dims('time')
                #Apply the operator
                elif thisInd['statistic']=='mean':
                    res=datPeriodSeason.mean(['time'],keep_attrs=True)
                else:
                    sys.exit('Unknown indicator statistic, "' + ind['statistic'] +'"')
                slices.append(res)
                periodIds.append(thisPeriod['id'])

        #Convert list back into dataset 
        dout=xr.concat(slices,dim='period')
        dout=dout.assign_coords(period=periodIds)

    #Time binning by defined units
    elif thisInd['time_binning'] in ['years','months']:
        #Then group by time
        if thisInd['time_binning']=="years":
            datGroupped=datSeason.resample(time="1Y",label="right")
        elif thisInd['time_binning']=="months":
            datGroupped=datSeason.resample(time="1M",label="right")
        else:
            sys.exit("Shouldn't be here")

        #Apply the operator
        if thisInd['statistic']=='mean':
            dout=datGroupped.mean(['time'],keep_attrs=True)
        else:
            sys.exit('Unknown indicator statistic, "' + thisInd['statistic'] +'"')

    else:
        sys.exit("Unknown time_binning method, '" + thisInd['time_binning']+ "'")

    #Polish final product and write
    dout.name='indicator'
    dout.to_netcdf(outFile[0])



