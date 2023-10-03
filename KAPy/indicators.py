import pickle
import xarray as xr
import os
import numpy as np

#config=KAPy.configs.loadConfig()
#indicator=config['indicators'][101]
#datPkl='./outputs/3.xarrays/fwi_EUR-11_NCC-NorESM1-M_rcp85_r1i1p1_MOHC-HadREM3-GA7-05_v1_day.pkl'

def calculateStatistics(indicator,config,outPath,datPkl):
    
    #Read pickle
    with open(datPkl[0],'rb') as f:
        thisDat=pickle.load(f)

    #Split dataset into time slices and calculate average 
    slices=[]
    periodIds=[]
    theseMonths=config['seasons'][indicator['season']]['months']
    for p in config['periods']:
            #Extract configuration
            thisPeriod=config['periods'][p]
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


