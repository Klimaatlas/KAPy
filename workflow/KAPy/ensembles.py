import xarray as xr
import numpy as np
import datetime


# Function to rename ensemble statistics once generated
def _renameEnsStats(d, suffix):
    for n in ["indicator", "delta"]:
        d = d.rename({f"{n}": f"{n}_{suffix}"})
    return d


def calculate_ensemble_statistics(input_files, percentiles, method):
    # Setup the ensemble
    # Given that all input files have been regridded onto a common grid,
    # they can then be concatenated into a single object. There are
    # two approachs. Previously we have used the create_ensemble from xclim.ensembles
    # However, this is quite fancy, and does a lot of logic about calendars that
    # create further problems. It also doesn't seem to handle cftime calendars at all well,
    # nor propigate attributes cleanly.
    # Instead, we do it all manually by directly opening the files with open_mfdataset, and then
    # loading it into RAM
    time_coder = xr.coders.CFDatetimeCoder(use_cftime=True)
    source_ensemble = xr.open_mfdataset(
        input_files,
        concat_dim="member",
        combine="nested",
        coords="all",
        decode_times=time_coder,
        decode_timedelta=False,
        join="outer",
    )
    source_ensemble = source_ensemble.compute()

    # For calculating ensemble statistics, we only need the indicator and delta variables
    # We therefore drop the other variables and add them back later
    ensemble_data = source_ensemble[["indicator", "delta"]]

    # Calculate number of ensemble members at each point
    ensN = (~np.isnan(ensemble_data)).sum(dim="member", keep_attrs=True)
    ensN = _renameEnsStats(ensN, "n")

    # Calculate the statistics
    ensMean = ensemble_data.mean(dim="member", keep_attrs=True)
    ensMean = _renameEnsStats(ensMean, "mean")
    ensSd = ensemble_data.std(dim="member", keep_attrs=True)
    ensSd = _renameEnsStats(ensSd, "standard_deviation")
    ensMax = ensemble_data.max(dim="member", keep_attrs=True)
    ensMax = _renameEnsStats(ensMax, "maximum")
    ensMin = ensemble_data.min(dim="member", keep_attrs=True)
    ensMin = _renameEnsStats(ensMin, "minimum")

    # Calculate the percentiles and transpose to a more friendly order
    ptileList = sorted(percentiles)
    qtileList = [x / 100 for x in ptileList]
    ensPercs = ensemble_data.quantile(
        q=qtileList, dim="member", method=method, keep_attrs=True, skipna=True
    )
    ensPercs = ensPercs.rename({"quantile": "percentiles"})
    ensPercs = ensPercs.assign_coords(percentiles=ptileList)

    # ensPercs = ensPercs.transpose("time", "season", "percentiles", ...)
    ensPercs = _renameEnsStats(ensPercs, "percentiles")

    # Combine results
    out = xr.merge([ensPercs, ensMean, ensSd, ensN, ensMax, ensMin])

    # Tidy up output-------------------
    # Restore auxiliary coordinates by copying them back into the original dataset.
    # This process is complicated a bit though by the fact that we have one version for each
    # member.
    # The season mask is first, and the easiest, as they are the same for all members.
    out["season_mask"] = source_ensemble["season_mask"].isel(member=0)
    # The time bounds are a bit more complicated, as they can differ between members
    out["time_bnds"] = source_ensemble["time_bnds"].isel(member=0)

    # Copy attributes
    out.attrs = source_ensemble.attrs

    # Add CF compliant bits here e.g history, and global attributes
    out.attrs.update(
        {
            "Conventions": "CF-1.9",
            "title": "KAPy indicator dataset",
            "history": (
                f"{datetime.datetime.now(datetime.timezone.utc).isoformat()} "
                f"Ensemble statistics calculated from {len(input_files)} simulations. Input file list recorded in source attribute."
            ),
        }
    )

    # Sort
    sorted_vars = sorted(out.data_vars)  # Get sorted variable names
    out = out[sorted_vars]  # Reorder dataset

    return out


# Development configuration----------------------------
if __name__ == "__main__":
    # Setup for debugging
    # ASSERT: working directory is the root of the project
    import KAPy

    config = KAPy.get_config("./config/config.yaml")
    wf = KAPy.get_workflow(config)
    output_file = list(wf["ensemble_statistics"]["input_dict"].keys())[0]
    input_files = wf["ensemble_statistics"]["input_dict"][output_file]
    print(f"Using input files: {input_files}")
    print(f"based on requirements for output file: {output_file}")

    # Run the function
    percentiles = [5, 95]
    method = "midpoint"
    out = calculate_ensemble_statistics(
        input_files=input_files, percentiles=percentiles, method=method
    )
    print("Success!")
