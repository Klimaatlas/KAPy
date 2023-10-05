import KAPy
import pickle
import xarray as xr
import os
import numpy as np
import sys

#config=KAPy.loadConfig()
#indicator=config['indicators'][101]
#datPkl=['./outputs/3.xarrays/fwi_EUR-11_NCC-NorESM1-M_rcp85_r1i1p1_MOHC-HadREM3-GA7-05_v1_day.pkl']

def calculateStatistics(indicator,config,outPath,datPkl):
    if config['time_averaging']['method'].lower()=='periods':
        KAPy.calculatePeriodStatistics(indicator,config,outPath,datPkl)
    elif config['time_averaging']['method'].lower() in ['year','month']:
        KAPy.calculateTimebinnedStatistics(indicator,config,outPath,datPkl)
    else:
        sys.exit("Unknown time_averaging method, '" + config['time_averaging']['method'] + "'")

def calculatePeriodStatistics(indicator,config,outPath,datPkl):
    
    #Read pickle
    with open(datPkl[0],'rb') as f:
        thisDat=pickle.load(f)

    #Split dataset into time slices and calculate average 
    slices=[]
    periodIds=[]
    theseMonths=config['seasons'][indicator['season']]['months']
    for thisPeriod in config['time_averaging']['periods'].values():
            #Filter by season first (should always work)
            datSeason=thisDat.sel(time=np.isin(thisDat.time.dt.month,theseMonths))
            #Slice dataset
            timemin=datSeason.time.dt.year >=thisPeriod['start']
            timemax=datSeason.time.dt.year <=thisPeriod['end']
            datPeriodSeason=datSeason.sel(time=timemin & timemax)
            #Apply the operator
            if indicator['statistic']=='mean':
                ind=datPeriodSeason.mean(['time'],keep_attrs=True)
            else:
                sys.exit('Unknown indicator statistic, "' + indicator['statistic'] +'"')
            slices.append(ind)
            periodIds.append(thisPeriod['id'])

    #Convert list back into dataset 
    dout=xr.concat(slices,dim='period')
    dout=dout.assign_coords(period=periodIds)
    dout=dout.rename({indicator['variables']:f"i{indicator['id']}"})  #Fix this up somehow

    #Write output
    dout.to_netcdf(outPath[0])

def calculateTimebinnedStatistics(indicator,config,outPath,datPkl):
    
    #Read pickle
    with open(datPkl[0],'rb') as f:
        thisDat=pickle.load(f)

    #Filter by season first (should always work)
    theseMonths=config['seasons'][indicator['season']]['months']
    datSeason=thisDat.sel(time=np.isin(thisDat.time.dt.month,theseMonths))
    #Then group by time
    if config['time_averaging']['method'].lower()=="year":
        datGroupped=datSeason.resample(time="1Y",label="right")
    elif config['time_averaging']['method'].lower()=="month":
        datGroupped=datSeason.resample(time="1M",label="right")
    else:
        sys.exit("Shouldn't be here")

    #Apply the operator
    if indicator['statistic']=='mean':
        ind=datGroupped.mean(['time'],keep_attrs=True)
    else:
        sys.exit('Unknown indicator statistic, "' + indicator['statistic'] +'"')

    #Tidy up
    dout=ind.rename({indicator['variables']:f"i{indicator['id']}"})  #Fix this up somehow

    #Write output
    dout.to_netcdf(outPath[0])

