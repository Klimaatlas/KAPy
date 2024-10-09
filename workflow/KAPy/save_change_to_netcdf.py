import xarray as xr

# Save cahnges from first period to rcp scenarios to netcdf -----------------------------------------------------------
"""
indicator_id = "102"
ensemble_stats_files = [/lustre/storeC-ext/users/klimakverna/development/KAPy/results ...
                        /4.ensstats/time_binning_periods/hadgem/102_CMIP5_historical_ensstats.nc,
                        /lustre/storeC-ext/users/klimakverna/development/KAPy/results ...
                        /4.ensstats/time_binning_periods/hadgem/102_CMIP5_rcp26_ensstats.nc,
                        /lustre/storeC-ext/users/klimakverna/development/KAPy/results ...
                        /4.ensstats/time_binning_periods/hadgem/102_CMIP5_rcp45_ensstats.nc
                        ]

output_files = [/lustre/storeC-ext/users/klimakverna/development/KAPy/results ...
                /7.netcdf/102_rcp26_change_periods.nc]
"""


def save_change_to_netcdf(
    config: dict, indicator_id: str, scenario: str, ensemble_stats_files: list[str], netcdf_filename=None
):
    indicator = config["indicators"][indicator_id]

    for filename in ensemble_stats_files:
        if scenario in filename:
            ds = xr.open_dataset(filename)
        elif "historical" in filename:
            ds_historical = xr.open_dataset(filename)

    change_ds_list = []
    historical_mean_values = ds_historical["indicator_mean"].isel(periodID=0).drop("periodID")
    periods = ["2", "3"]

    for period in periods:
        try:
            current_ds = xr.Dataset(ds.sel(periodID=period)).drop("periodID")
        except KeyError:
            current_ds = xr.Dataset(ds.sel(periodID=int(period))).drop("periodID")
        indicator_mean_change = current_ds["indicator_mean"] - historical_mean_values
        indicator_mean_relative_change = indicator_mean_change * 100 / historical_mean_values
        change_ds_list.append(
            current_ds.assign(
                indicator_mean_change=indicator_mean_change.expand_dims("periodID"),
                indicator_mean_relative_change=indicator_mean_relative_change.expand_dims("periodID"),
            )
        )

    change_ds = xr.concat(change_ds_list, "periodID")
    change_ds = change_ds.assign(periodID=[2, 3])
    # change_ds["periodID"].astype("int")  # for cdo infon to not throw error

    attrs = ds.attrs
    attrs["units"] = indicator["units"]
    attrs["name"] = indicator["name"]
    attrs["scenario"] = scenario
    change_ds = change_ds.assign_attrs(attrs)
    change_ds["indicator_mean_relative_change"].attrs = {"units": "%"}

    change_ds.to_netcdf(netcdf_filename[0])
