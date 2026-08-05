"""
Indicators.py

Given one or more climate variables, the functions here will calculate indicators, with time binning either across
defined periods or annual time bins.
"""

import xarray as xr
import xclim as xc
import numpy as np
import cftime
import datetime

# Use absolute imports assuming KAPy is installed
from KAPy import helpers

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
    description,
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
    time_bounds = []
    if time_binning == "periods":
        period_slice_list = []
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
            season_slice_list = []
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
                        # Apply operator
                        res = stat_function(**datDict, **stat_args)
                        # Check that the result is either a DataArray or a Dataset
                        if not (
                            isinstance(res, xr.DataArray) or isinstance(res, xr.Dataset)
                        ):
                            raise TypeError(
                                f"The custom function '{custom_function}' returned an object of type {type(res)} instead of a DataArray or Dataset. Please check the custom function."
                            )
                    else:
                        res = stat_function(datPeriodSeason, **stat_args)
                    res["season"] = thisSeason
                    season_slice_list.append(res)

            # Concatenate seasons into a dataarray and store
            outSeason = xr.concat(season_slice_list, dim="season")
            period_slice_list.append(outSeason)

            # Store metadata
            time_bounds.append(
                [
                    cftime.DatetimeGregorian(int(thisPeriod["start"]), 1, 1),
                    cftime.DatetimeGregorian(int(thisPeriod["end"]) + 1, 1, 1),
                ]
            )

        # Concatenate across periods now
        indicators = xr.concat(period_slice_list, dim="time")

    # Time binning by years
    # ----------------------------
    elif time_binning in ["years"]:
        # Loop over seasons
        seasonTimeseries = []
        for thisSeason in indSeasons:
            # Filter data by season
            theseMonths = seasonsTable[thisSeason]["months"]
            datSeason = thisDat.sel(time=np.isin(thisDat.time.dt.month, theseMonths))

            # Then group by time.
            datGroupped = datSeason.resample(time="YS")

            # Apply the operator
            if statistic == "custom":
                # split the Xarray dataset into a dict again for passing
                if isinstance(thisDat, xr.DataArray):
                    datDict = {list(input_files.keys())[0]: datGroupped}
                elif isinstance(thisDat, xr.Dataset):
                    datDict = {
                        thisKey: datGroupped[thisKey] for thisKey in input_files.keys()
                    }
                else:
                    raise TypeError(
                        "Unknown data type for datGroupped. Expected DataArray or Dataset."
                    )
                # Apply operator
                res = stat_function(**datDict, **stat_args)
                # Check that the result is either a DataArray or a Dataset
                if not (isinstance(res, xr.DataArray) or isinstance(res, xr.Dataset)):
                    raise TypeError(
                        f"The custom function '{custom_function}' returned an object of type {type(res)} instead of a DataArray or Dataset. Please check the custom function."
                    )
            else:
                res = stat_function(datGroupped, **stat_args)
            # Store the results
            res["season"] = thisSeason
            seasonTimeseries.append(res)

        # Concatenate across seasons
        indicators = xr.concat(seasonTimeseries, dim="season")

        # Tidy metadata
        indicators.season.attrs["name"] = "season"

        # Handle time binds. We set time as midpoint of year, using the gregorian calendar
        # and the bounds to reflect the CF time bounds convention [start,end).
        # Note that we need to ensure cftime representation, for runs that
        # go out paste 2262
        time_bounds = [
            [
                cftime.DatetimeGregorian(x.dt.strftime("%Y"), 1, 1),
                cftime.DatetimeGregorian(int(x.dt.strftime("%Y")) + 1, 1, 1),
            ]
            for x in indicators.time
        ]

    else:
        raise ValueError(f"Unknown time binning method, '{time_binning}'.")

    # Establish variable ordering to be CF compliant: U-T-Z-Y-X
    indicators = indicators.transpose("season", "time", ...)

    # Calculation of changes
    # ------------------------
    # First we need the values for the reference period. That's easy for
    # period binning, but we need to calculate it for annual binning
    if time_binning == "periods":
        # We use the first periodID as the reference here
        ref = indicators.isel(time=0)
    elif time_binning in ["years"]:
        # Again use the first time period, but average
        refPeriod = list(periodsTable.values())[0]
        refDat = helpers.timeslice(indicators, refPeriod["start"], refPeriod["end"])
        ref = refDat.mean(dim="time")
    else:
        raise ValueError(f"Unknown time binning method, '{time_binning}'.")

    # Calculate change
    if delta_type == "subtract":
        deltas = indicators - ref
    elif delta_type == "divide":
        deltas = indicators / ref
    else:
        raise ValueError(f"Unknown delta_type method, '{delta_type}'.")

    # Polish final product
    # ----------------------
    # Generate time mid points and time bounds auxiliary coordinate
    mid_times = [
        start_time + (end_time - start_time) / 2 for start_time, end_time in time_bounds
    ]

    # Generate season mask
    season_ids = list(seasonsTable.keys())
    months = np.arange(1, 13).astype("int32")
    season_mask = np.zeros((len(season_ids), len(months)), dtype=np.int8)
    for i, season_id in enumerate(season_ids):
        for month in seasonsTable[season_id]["months"]:
            season_mask[i, month - 1] = 1

    # The final product requires a reshuffle. We currently have one object with the absolute values for each
    # indicator, and one with the delta change, for each indicator. We want to rejig this so that
    # we have a dataset for each indcator, containing both the absolute and delta change variables.
    # For easy handling, we store this in a dict, which is the ultimate output of the function
    # We also need to be careful about the difference between datasets and dataarrays, which
    # both are legal at this point
    def _decorate_dataset(ds):

        # Time coordinate
        ds = ds.assign_coords({"time": ("time", mid_times)})
        ds.time.attrs["bounds"] = "time_bnds"
        ds.time.encoding["units"] = "days since 1970-01-01"
        ds.time.attrs.update(
            {
                "standard_name": "time",
                "long_name": "mid-point of time-bin used for indicator calculation",
                "axis": "T",
            }
        )
        ds.time.encoding["_FillValue"] = None

        # Time bounds
        ds["time_bnds"] = xr.DataArray(time_bounds, dims=("time", "nv"))
        ds["time_bnds"].encoding.pop("_FillValue", None)

        # Season coordinate
        ds = ds.assign_coords({"season": ("season", np.array(season_ids, dtype=str))})
        ds.season.attrs["long_name"] = (
            "identifier for the season mask used for indicator calculation"
        )

        # Month coordinate
        ds = ds.assign_coords({"month": ("month", months)})
        ds["month"].attrs.update(
            {
                "long_name": "calendar month",
                "valid_min": np.int32(1),
                "valid_max": np.int32(12),
            }
        )
        # Season mask
        ds["season_mask"] = xr.DataArray(season_mask, dims=("season", "month"))
        ds["season_mask"].attrs.update(
            {
                "long_name": "season definition mask",
                "description": "Boolean mask indicating whether a calendar month is included in the season",
                "flag_values": np.array([0, 1], dtype=np.int8),
                "flag_meanings": "not_included included",
            }
        )

        # Delta attributes
        ds.delta.attrs = {
            "long_name": "change in indicator value relative to first time-bin",
            "delta_type": delta_type,
        }

        # Indicator attributes
        ds.indicator.attrs = {
            "long_name": "indicator value calculated over time-bin",
            "description": description,
        }

        # Global attributes
        ds.attrs = {
            "title": "KAPy indicator dataset",
            "Conventions": "CF-1.9",
            "history": (
                f"{datetime.datetime.now(datetime.timezone.utc).isoformat()} "
                "Indicator calculation performed using KAPy."
            ),
            "time_binning": time_binning,
            "statistic": statistic,
            "additional_arguments": str(additional_arguments),
            "custom_script": custom_script,
            "custom_function": custom_function,
        }

        # Sort
        ds = ds[sorted(ds.data_vars)]

        return ds

    # Apply the decoration function
    if isinstance(indicators, xr.Dataset):
        rtn = {}
        for v in list(indicators.data_vars):
            # Extract indicators and merge into a dataset
            out = xr.Dataset({"indicator": indicators[v], "delta": deltas[v]})
            # Add attributes and store
            out = _decorate_dataset(out)
            rtn[v] = out

    elif isinstance(indicators, xr.DataArray):
        out = xr.Dataset({"indicator": indicators, "delta": deltas})
        rtn = _decorate_dataset(out)

    return rtn


# Development configuration----------------------------
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

    # Test full function  ------------------------
    tas = "outputs/01.primary_variables/CORDEX-tas-44/CORDEX_tas_AFR-44_historical+rcp85_NCC-NorESM1-M_r1i1p1_SMHI-RCA4_v1_mon_Ghana-44.pkl"
    input_files = {"tas": tas}
    seasonsTable = {
        "JJA": {
            "months": [6, 7, 8],
            "description": "Summer (JJA)",
        }
    }
    periodsTable = {
        "2013": {"id": "2013", "start": "2013", "end": "2013"},
        "2014": {"id": "2014", "start": "2014", "end": "2014"},
    }
    seasons = ["JJA"]
    time_binning = "years"
    statistic = "mean"
    skipna = False
    delta_type = "subtract"
    additional_arguments = {}
    custom_script = ""
    custom_function = ""
    description = "test"

    out = calculate_indicators(
        input_files=input_files,
        seasonsTable=seasonsTable,
        periodsTable=periodsTable,
        seasons=seasons,
        time_binning=time_binning,
        statistic=statistic,
        skipna=skipna,
        delta_type=delta_type,
        additional_arguments=additional_arguments,
        custom_script=custom_script,
        custom_function=custom_function,
        description=description,
    )

    # Test custom function returning multiple indicators
    statistic = "custom"
    time_binning = "years"
    custom_script = "workflow/testing/hotdays.py"
    custom_function = "hotdays"
    description = "test"
    out = calculate_indicators(
        input_files=input_files,
        seasonsTable=seasonsTable,
        periodsTable=periodsTable,
        seasons=seasons,
        time_binning=time_binning,
        statistic=statistic,
        skipna=skipna,
        delta_type=delta_type,
        additional_arguments=additional_arguments,
        custom_script=custom_script,
        custom_function=custom_function,
        description=description,
    )
