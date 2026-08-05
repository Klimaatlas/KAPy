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


def hotdays(tas: xr.DataArray, **kwargs) -> xr.Dataset:
    # Calculate number of days above 30
    # Note that we need to handle the case where tas is a grouped object,
    # differently to the ungrouped case
    if isinstance(tas, xr.core.resample.Resample):
        t30 = tas.map(lambda x: (x > 30).sum("time"))
    else:
        t30 = (tas > 30).groupby("time.year").sum("time").mean("year")
    t30.attrs["long_name"] = "Days per year above 30 C"
    t30.attrs["units"] = "Days per year"

    # And above 25
    if isinstance(tas, xr.core.resample.Resample):
        t25 = tas.map(lambda x: (x > 25).sum("time"))
    else:
        t25 = (tas > 25).groupby("time.year").sum("time").mean("year")
    t25.attrs["long_name"] = "Days per year above 25 C"
    t25.attrs["units"] = "Days per year"

    res = xr.Dataset({"T30": t30, "T25": t25})

    return res


# Validation----------------
if __name__ == "__main__":

    # Load xarray tutotrial data and convert to degrees C.
    air_temp = xr.tutorial.load_dataset("air_temperature")
    tas = air_temp.air.resample(time="D").mean() - 273.15

    # Apply function
    ds = hotdays(tas)

    # Make plots
    import matplotlib.pyplot as plt

    ds.T30.plot()
    plt.show()
    ds.T25.plot()

    # Test with grouped data
    tas = tas.resample(time="YS")
    ds = hotdays(tas)
