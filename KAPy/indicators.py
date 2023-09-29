import pickle
import xarray as xr
import os

#config=KAPy.helpers.loadConfig()

def index101(datPkl,outPath,config):
    #datPkl='./scratch/xarray_datasets/tas_AFR-22_MOHC-HadGEM2-ES_rcp85_r1i1p1_CLMcom-KIT-CCLM5-0-15_v1_mon.pkl'

    #Read pickle
    with open(datPkl,'rb') as f:
        thisDat=pickle.load(f)

    #Split dataset into time slices and calculate
    #average temperature
    slices=[]
    periodIds=[]
    for p in config['periods']:
        #Extract period
        thisPeriod=config['periods'][p]
        #Slice dataset
        timemin=thisDat.time.dt.year >=thisPeriod['start']
        timemax=thisDat.time.dt.year <=thisPeriod['end']
        datSlice=thisDat.sel(time=timemin & timemax)
        #Calculate the average
        datMean=datSlice.mean(['time'],keep_attrs=True)
        slices.append(datMean)
        periodIds.append(thisPeriod['id'])

    #Convert list back into dataset 
    dout=xr.concat(slices,dim='period')
    dout=dout.assign_coords(period=periodIds)
    dout=dout.rename({'tas':'i101'})

    #Write output
    dout.to_netcdf(outPath)


