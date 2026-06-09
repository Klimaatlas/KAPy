"""
hotdays.py

Simple demonstration script showing how an arbitrary indicator can be calculated - in
this case, the number of days above two temperature thresholds degrees. This indicator is better calculated via
the count statistic, but this script shows how it can be implemented by hand.

Parameters
----------
tas : xr.DataArray
    Daily averaged temperature, in degrees C.

Additional keyword arguments (kwargs) e.g. skipna are accepted but ignored.    

Returns
-------
xr.Dataset
    Mean number of days per year above 20 (T20) and 25 (T25) degrees C.

"""
import xarray as xr

def hotdays(tas: xr.DataArray,**kwargs) -> xr.Dataset:
    #Calculate number of days above 20
    t20 = tas > 20
    t20.attrs["long_name"]="Days per year above 20 C"
    t20.attrs["units"]="Days per year"

    #And above 25
    t25 = tas > 25
    t25.attrs["long_name"]= "Days per year above 25 C"
    t25.attrs["units"]="Days per year"
    combined=xr.Dataset({"T20":t20,"T25":t25})
    res=combined.groupby("time.year").sum().mean(dim="year")
    
    return res


# Validation----------------
if __name__ == "__main__":
    
    #Load xarray tutotrial data and convert to degrees C.
    air_temp = xr.tutorial.load_dataset("air_temperature")
    tas = air_temp.air.resample(time="D").mean() - 273.15

    #Apply function
    ds=hotdays(tas)

    #Make plots
    import matplotlib.pyplot as plt
    ds.T20.plot()
    plt.show()
    ds.T25.plot()

