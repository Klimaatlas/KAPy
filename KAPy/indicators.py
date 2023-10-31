import KAPy
import pickle
import xarray as xr
import os
import numpy as np
import sys

#config=KAPy.loadConfig()
#indicatorKey='101y'
#datPkl=['./KAGh/3.datasets/tas_AFR-22_MOHC-HadGEM2-ES_rcp26_r1i1p1_CLMcom-KIT-CCLM5-0-15_v1_mon.nc.pkl']
#datPkl=['./DKHav/3.datasets/tas_nsbs_EUR-11_ICHEC-EC-EARTH_rcp45_r12i1p1_SMHI-RCA4_v4_day.nc.pkl']

def calculateIndicators(thisInd,config,outPath,datPkl):
    
    #Read pickle
    with open(datPkl[0],'rb') as f:
        thisDat=pickle.load(f)

    #Filter by season first (should always work)
    theseMonths=config['seasons'][thisInd['season']]['months']
    datSeason=thisDat.sel(time=np.isin(thisDat.time.dt.month,theseMonths))
        
    #Time averaing over periods
    if thisInd['time_averaging'].lower()=='periods':
        slices=[]
        periodIds=[]
        for thisPeriod in config['periods'].values():
                #Slice dataset
                timemin=datSeason.time.dt.year >=thisPeriod['start']
                timemax=datSeason.time.dt.year <=thisPeriod['end']
                datPeriodSeason=datSeason.sel(time=timemin & timemax)
                #Apply the operator
                if thisInd['statistic']=='mean':
                    res=datPeriodSeason.mean(['time'],keep_attrs=True)
                else:
                    sys.exit('Unknown indicator statistic, "' + ind['statistic'] +'"')
                slices.append(res)
                periodIds.append(thisPeriod['id'])

        #Convert list back into dataset 
        dout=xr.concat(slices,dim='period')
        dout=dout.assign_coords(period=periodIds)

    #Time averaging by defined units
    elif thisInd['time_averaging'].lower() in ['year','month']:
        #Then group by time
        if thisInd['time_averaging'].lower()=="year":
            datGroupped=datSeason.resample(time="1Y",label="right")
        elif thisInd['time_averaging'].lower()=="month":
            datGroupped=datSeason.resample(time="1M",label="right")
        else:
            sys.exit("Shouldn't be here")

        #Apply the operator
        if thisInd['statistic']=='mean':
            dout=datGroupped.mean(['time'],keep_attrs=True)
        else:
            sys.exit('Unknown indicator statistic, "' + thisInd['statistic'] +'"')

    else:
        sys.exit("Unknown time_averaging method, '" + config['time_averaging']['method'] + "'")

    #Polish final product and write
    dout=dout.rename({thisInd['variables']:"indicator"})  #Fix this up somehow
    dout.to_netcdf(outPath[0])



