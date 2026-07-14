"""
Indicators.py

Given one or more climate variables, the functions here will calculate indicators, with time binning either across
defined periods or annual time bins. 
"""

import xarray as xr
import xclim as xc
import numpy as np
import cftime
import json

try:  # Differentiate between importing when in a module and running the script locally
    from . import helpers
except ImportError:
    import helpers

# Private functions-------------------------


def _stat_mean(d: xr.DataArray, skipna: bool) -> xr.DataArray:
    return d.mean("time", keep_attrs=True, skipna=skipna)


def _stat_mean(d: xr.DataArray, skipna: bool) -> xr.DataArray:
    return d.mean("time", keep_attrs=True, skipna=skipna)


def _stat_max(d: xr.DataArray, skipna: bool) -> xr.DataArray:
    return d.max("time", keep_attrs=True, skipna=skipna)


def _stat_min(d: xr.DataArray, skipna: bool) -> xr.DataArray:
    return d.min("time", keep_attrs=True, skipna=skipna)


def _stat_meanmax(d: xr.DataArray, skipna: bool) -> xr.DataArray:
    return (
        d.groupby("time.year")
        .max(skipna=skipna)
        .mean(dim="year", keep_attrs=True, skipna=skipna)
    )


def _stat_meanmin(d: xr.DataArray, skipna: bool) -> xr.DataArray:
    return (
        d.groupby("time.year")
        .min(skipna=skipna)
        .mean(dim="year", keep_attrs=True, skipna=skipna)
    )


def _stat_count(
    d: xr.DataArray, op: str, threshold: float, skipna: bool
) -> xr.DataArray:
    # Do count
    comp = xc.indices.generic.compare(left=d, op=op, right=threshold)
    # Python doesn't handle comparisons against NaNs very nicely: NaN > 0 returns false (rather than NaN)
    # We work around this by reinserting nans into the comparison array
    # Note that we apply a minimum count criteria in the first summation step - everything is
    # NaN, then we want to get NaN, rather than 0.
    comp = comp.astype("int8").where(d.notnull(), np.nan)
    res = (
        comp.groupby("time.year")
        .sum(skipna=skipna, min_count=1)
        .mean(dim="year", skipna=skipna)
    )
    return res


def _stat_quantile(d: xr.DataArray, qtile: float, skipna: bool) -> xr.DataArray:
    return d.quantile(q=qtile, dim="time", skipna=skipna).drop_vars("quantile")


# Public functions-----------------------------------------------------


def calculate_indicators(
    input_files,
    seasonsTable,
    periodsTable,
    seasons,
    time_binning,
    statistic,
    skipna,
    delta_type,
    additional_arguments,
    custom_script,
    custom_function,
    **kwargs,
):

    # Setup seasons
    if "all" in seasons:
        indSeasons = list(seasonsTable.keys())
    else:
        indSeasons = seasons

    # Read the relevant datasets back from disk and build into a dataset
    # If there is only one input variable, keep it all as a dataarray - otherwise,
    # merge it a dataset to take advantage of the overloaded time slicing functions of Xarray.
    # However, we also want to enforce passing by named arguments to our custom function and therefore
    # split the Xarray dataset into a dict again at a later point
    if len(input_files) == 1:
        thisDat = helpers.read_file(next(iter(input_files.values())))
    else:
        thisDat = xr.Dataset(
            {
                thisKey: helpers.read_file(thisPath)
                for thisKey, thisPath in input_files.items()
            }
        )

    # Get statistical operator
    if statistic == "mean":
        stat_function = _stat_mean
        stat_args = {"skipna": skipna}
    elif statistic == "max":
        stat_function = _stat_max
        stat_args = {"skipna": skipna}
    elif statistic == "min":
        stat_function = _stat_min
        stat_args = {"skipna": skipna}
    elif statistic == "meanmax":
        stat_function = _stat_meanmax
        stat_args = {"skipna": skipna}
    elif statistic == "meanmin":
        stat_function = _stat_meanmin
        stat_args = {"skipna": skipna}
    elif statistic == "count":
        stat_function = _stat_count
        # Check input arguments
        if not (("op" in additional_arguments) & ("threshold" in additional_arguments)):
            raise ValueError(
                "The 'additional_arguments' field must contain both 'op' and 'threshold' when using the 'count' statistic. "
            )
        try:
            threshold = float(additional_arguments["threshold"])
        except ValueError:
            raise ValueError(
                f"Cannot convert 'threshold' value in 'additional_arguments' to a float. 'Threshold' string value: {additional_arguments['threshold']}"
            )
        stat_args = {
            "op": additional_arguments["op"],
            "threshold": threshold,
            "skipna": skipna,
        }
    elif statistic == "quantile":
        stat_function = _stat_quantile
        # Check input arguments
        if "q" not in additional_arguments:
            raise ValueError(
                "The 'additional_arguments' field must define the quantile via the 'q' argument e.g q:0.5 "
            )
        try:
            qtile = float(additional_arguments["q"])
        except ValueError:
            raise ValueError(
                f"Cannot convert 'q' value in 'additional_arguments' to a float. 'q' string value: {additional_arguments['q']}"
            )
        stat_args = {"qtile": qtile, "skipna": skipna}
    elif statistic == "custom":
        # Retrieve the custom function. We check that the signature of the function
        # can accept at least the variables that we want
        stat_function = helpers.get_external_function(custom_script, custom_function)
        try:
            helpers.check_signature(stat_function, input_files)
        except ValueError as e:
            raise ValueError(
                f"Error in the signature of the external function '{custom_function}' "
                f"in '{custom_script}': {e}"
            ) from None

        # Addition args are just passed directly to the function
        stat_args = additional_arguments
        stat_args["skipna"] = skipna
    else:
        raise ValueError(f"Unknown indicator statistic, '{statistic}'")

    # Time binning over periods
    # ----------------------------------
    if time_binning == "periods":
        periodSlices = []
        for thisPeriod in periodsTable.values():
            # Slice dataset by time
            # It is possible that we end with an empty slice at this stage e.g. when
            # working with observations, but with time slices in the future. We handle
            # that case further one, as we still want empty slices returned
            datPeriod = helpers.timeslice(
                thisDat, thisPeriod["start"], thisPeriod["end"]
            )

            # If datPeriod is empty e.g. due to a timeslice that is outside
            # #of the domain, then trying to filter by months will
            # just cause things to break. So, only proceed with the processing if there
            # is something to filter
            if datPeriod.time.size == 0:
                continue

            # Loop over seasons
            seasonSlices = []
            for thisSeason in indSeasons:
                # Select seeason
                theseMonths = seasonsTable[thisSeason]["months"]
                datPeriodSeason = datPeriod.sel(
                    time=np.isin(datPeriod.time.dt.month, theseMonths)
                )

                # Only attempt a calculation if there is something left
                if datPeriodSeason.time.size != 0:
                    if statistic == "custom":
                        # split the Xarray dataset into a dict again for passing
                        if isinstance(datPeriodSeason, xr.DataArray):
                            datDict = {list(input_files.keys())[0]: datPeriodSeason}
                        elif isinstance(datPeriodSeason, xr.Dataset):
                            datDict = {
                                thisKey: datPeriodSeason[thisKey]
                                for thisKey in input_files.keys()
                            }
                        # Apply operator and store
                        res = stat_function(**datDict, **stat_args)
                    else:
                        res = stat_function(datPeriodSeason, **stat_args)
                    res["seasonID"] = thisSeason
                    seasonSlices.append(res)

            # Concatenate seasons into a dataarray and store
            outSeason = xr.concat(seasonSlices, dim="seasonID")
            outSeason["periodID"] = thisPeriod["id"]
            periodSlices.append(outSeason)

        # Concatenate across periods now
        dout = xr.concat(periodSlices, dim="periodID")

        # Tidy metadata
        dout.periodID.attrs["name"] = "periodID"
        dout.seasonID.attrs["name"] = "seasonID"

    # Time binning by years
    # ----------------------------
    elif time_binning in ["years"]:
        # Loop over seasons
        seasonTimeseries = []
        for thisSeason in indSeasons:
            # Filter data by season
            theseMonths = seasonsTable[thisSeason]["months"]
            datSeason = thisDat.sel(time=np.isin(thisDat.time.dt.month, theseMonths))

            # Then group by time. Could consider using groupby as an alternative
            datGroupped = datSeason.resample(time="YS")

            # Apply the operator
            if statistic == "custom":
                # split the Xarray dataset into a dict again for passing
                if isinstance(datGroupped, xr.DataArray):
                    datDict = {list(input_files.keys())[0]: datGroupped}
                elif isinstance(datGroupped, xr.Dataset):
                    datDict = {
                        thisKey: datGroupped[thisKey] for thisKey in input_files.keys()
                    }
                # Apply operator and store
                res = stat_function(**datDict, **stat_args)
            else:
                res = stat_function(datGroupped, **stat_args)
            # Store the results
            res["seasonID"] = thisSeason
            seasonTimeseries.append(res)

        # Concatenate across periods now
        dout = xr.concat(seasonTimeseries, dim="seasonID")
        dout = dout.transpose("time", "seasonID", ...)

        # Tidy metadata
        dout.seasonID.attrs["name"] = "seasonID"

        # Round time to the first day of the year. This ensures that everything
        # has an identical datetime, regardless of the calendar being used.
        # Kudpos to ChatGPT for this little work around
        # Note that we need to ensure cftime representation, for runs that
        # go out paste 2262
        dout["time"] = [
            cftime.DatetimeGregorian(x.dt.strftime("%Y"), x.dt.strftime("%m"), 1)
            for x in dout.time
        ]
    else:
        raise ValueError(f"Unknown time binning method, '{time_binning}'.")

    # Calculation of changes
    # ------------------------
    # First we need the values for the reference period. That's easy for
    # period binning, but we need to calculate it for annual binning
    if time_binning == "periods":
        # We use the first periodID as the reference here
        ref = dout.isel(periodID=0)
    elif time_binning in ["years"]:
        # Again use the first time period, but average
        refPeriod = list(periodsTable.values())[0]
        refDat = helpers.timeslice(dout, refPeriod["start"], refPeriod["end"])
        ref = refDat.mean(dim="time")
    else:
        raise ValueError(f"Unknown time binning method, '{time_binning}'.")

    # Calculate change
    if delta_type == "subtract":
        deltaOut = dout - ref
    elif delta_type == "divide":
        deltaOut = dout / ref
    else:
        raise ValueError(f"Unknown delta_type method, '{delta_type}'.")
    deltaOut.attrs["delta_type"] = delta_type

    # Polish final product
    # ----------------------
    # Firstly, we need a reshuffle. We currently have one object with the absolute values for each
    # indicator, and one with the delta change, for each indicator. We want to rejig this so that
    # we have object for each indcator, containing both the absolute and delta change variables.
    # For easy handling, we store this in a dict, which is the ultimate output of the function
    # We also need to be careful about the difference between datasets and dataarrays, which
    # both are legal at this point
    def decorate_dataset(ds):
        ds.attrs = {}
        ds.attrs["time_binning"] = time_binning
        ds.attrs["statistic"] = statistic
        ds.attrs["delta_type"] = delta_type
        ds.attrs["additional_arguments"] = str(additional_arguments)
        ds.attrs["custom_script"] = custom_script
        ds.attrs["custom_function"] = custom_function
        ds.attrs["seasonID_dict"] = json.dumps(seasonsTable)
        if time_binning == "periods":
            ds.attrs["periodID_dict"] = json.dumps(periodsTable)
        return ds

    if isinstance(dout, xr.Dataset):
        rtn = {}
        for v in list(dout.data_vars):
            # Extract indicators and merge into a dataset
            absolute_ind = dout[v]
            delta_ind = deltaOut[v]
            out = xr.Dataset({"indicator": absolute_ind, "delta": delta_ind})
            # Add attributes and store
            out = decorate_dataset(out)
            rtn[v] = out

    elif isinstance(dout, xr.DataArray):
        out = xr.Dataset({"indicator": dout, "delta": deltaOut})
        rtn = decorate_dataset(out)

    return rtn


# Validation ----------------------------
if __name__ == "__main__":
    # Setup for debugging
    import matplotlib.pyplot as plt

    # Load xarray tutotrial data and convert to degrees C.
    air_temp = xr.tutorial.load_dataset("air_temperature")
    tas = air_temp.air.resample(time="D").mean() - 273.15

    # Add some stripes of NaNs to test response to NaNs
    tas[0, 10, :] = np.nan  # Set a horizontal band in first time slice
    tas[:, :, 25] = np.nan  # Set a vertical band across all time steps
    # View
    tas.isel(time=0).plot()
    plt.show()
    tas.isel(time=1).plot()
    plt.show()

    # Now iterate over the operators and plot
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(
        nrows=7,
        ncols=2,
        figsize=(12, 28),
        constrained_layout=True,
    )

    plots = [
        ("Mean", lambda s: _stat_mean(tas, skipna=s)),
        ("Max", lambda s: _stat_max(tas, skipna=s)),
        ("Min", lambda s: _stat_min(tas, skipna=s)),
        ("Meanmax", lambda s: _stat_meanmax(tas, skipna=s)),
        ("Meanmin", lambda s: _stat_meanmin(tas, skipna=s)),
        ("Count > 0", lambda s: _stat_count(tas, skipna=s, op="gt", threshold=0)),
        ("95th pct", lambda s: _stat_quantile(tas, skipna=s, qtile=0.95)),
    ]

    for row, (name, func) in enumerate(plots):

        func(True).plot(ax=axes[row, 0])
        axes[row, 0].set_title(f"{name} - skipna={True}")

        func(False).plot(ax=axes[row, 1])
        axes[row, 1].set_title(f"{name} - skipna={False}")

    plt.show()
