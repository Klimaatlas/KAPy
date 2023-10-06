import KAPy
import pickle
import xarray as xr
import os
import numpy as np
import sys

#config=KAPy.loadConfig()
#indicator=config['indicators'][101]
#datPkl=['./outputs/3.xarrays/fwi_EUR-11_NCC-NorESM1-M_rcp85_r1i1p1_MOHC-HadREM3-GA7-05_v1_day.pkl']

def calculateIndicators(indicator,config,outPath,datPkl):
    #Read pickle
    with open(datPkl[0],'rb') as f:
        thisDat=pickle.load(f)

    #Filter by season first (should always work)
    theseMonths=config['seasons'][indicator['season']]['months']
    datSeason=thisDat.sel(time=np.isin(thisDat.time.dt.month,theseMonths))
        
    #Time averaing over periods
    if indicator['time_averaging'].lower()=='periods':
        slices=[]
        periodIds=[]
        for thisPeriod in config['periods'].values():
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

    #Time averaging by defined units
    elif indicator['time_averaging'].lower() in ['year','month']:
        #Then group by time
        if indicator['time_averaging'].lower()=="year":
            datGroupped=datSeason.resample(time="1Y",label="right")
        elif indicator['time_averaging'].lower()=="month":
            datGroupped=datSeason.resample(time="1M",label="right")
        else:
            sys.exit("Shouldn't be here")

        #Apply the operator
        if indicator['statistic']=='mean':
            dout=datGroupped.mean(['time'],keep_attrs=True)
        else:
            sys.exit('Unknown indicator statistic, "' + indicator['statistic'] +'"')

    else:
        sys.exit("Unknown time_averaging method, '" + config['time_averaging']['method'] + "'")

    #Polish final product and write
    dout=dout.rename({indicator['variables']:f"i{indicator['id']}"})  #Fix this up somehow
    dout.to_netcdf(outPath[0])



