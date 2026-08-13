import xarray as xr
import numpy as np
import datetime
from scipy.stats import norm

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
    # loading it into RAM.
    # Note also that we don't decode times initially but handle this process explicitly later
    source_ensemble = xr.open_mfdataset(
        input_files,
        concat_dim="member",
        combine="nested",
        coords="all",
        decode_times=False,
        decode_timedelta=False,
        join="outer",
    )
    source_ensemble = source_ensemble.compute()

    #Now handle the time_bounds variable - all time bounds should be the same if they
    #are present, so we can just take the maximum. But just to be sure, we also
    #take the minimum as well - checking that the two are the same is tells us
    #if there is anything wierd going on
    max_time_bounds = source_ensemble["time_bnds"].max(dim="member", skipna=True) 
    min_time_bounds = source_ensemble["time_bnds"].min(dim="member", skipna=True)  
    if not (max_time_bounds == min_time_bounds).all():
        raise ValueError("time_bnds differ between ensemble members")
    source_ensemble["time_bnds"] = max_time_bounds

    #And now we can decode the times to cftime objects
    time_coder = xr.coders.CFDatetimeCoder(use_cftime=True)
    source_ensemble = xr.decode_cf(source_ensemble,
                                   decode_times=time_coder)

    # For calculating ensemble statistics, we only need the indicator and delta variables
    # We therefore drop the other variables and add them back later
    ensemble_data = source_ensemble[["indicator", "delta"]]

    # Calculate number of ensemble members at each point
    ensN = (~np.isnan(ensemble_data)).sum(dim="member", keep_attrs=True)
    ensN = _renameEnsStats(ensN, "n")

    # Calculate the statistics
    ensMean = ensemble_data.mean(dim="member", keep_attrs=True)
    ensSd = ensemble_data.std(dim="member", keep_attrs=True)
    ensMax = ensemble_data.max(dim="member", keep_attrs=True)
    ensMin = ensemble_data.min(dim="member", keep_attrs=True)

    # Calculate the percentiles
    ptileList = sorted(percentiles)
    qtileList = [x / 100 for x in ptileList]
    if method == "parametric":  # Derive quantiles from the mean and standard deviation
        if (0 in ptileList == 0) or (100 in ptileList):
            raise ValueError(
                (
                    "Percentile list cannot contain 0 or 100 when using the"
                    f"'parametric' method but received values {percentiles}. "
                    "Please use another method if you are interested in"
                    "the ensemble maximum or minimum."
                )
            )
        z_scores = [norm.ppf(q) for q in qtileList]
        percentile_list = [ensMean + z * ensSd for z in z_scores]
        ensPercs = xr.concat(percentile_list, dim="percentiles")
        ensPercs = ensPercs.assign_coords(percentiles=ptileList)

    else:  
        # array.quantile can be painfully slow as it is not vectorized (?), so we use 
        # the np.quantile method directly from numpy instead. 
    
        #Loop over variables and compute quantiles
        percentiles_by_variable = {}
        for name, da in ensemble_data.data_vars.items():
            member_axis = da.get_axis_num("member")
    
            # result shape is (n_quantiles, *remaining_dims)
            values = np.quantile(da.values, qtileList, axis=member_axis, method=method)
    
            new_dims = ("percentiles",) + tuple(d for d in da.dims if d != "member")
    
            # keep other coords 
            new_coords = {
                k: v for k, v in da.coords.items() if "member" not in v.dims
            }
    
            percentiles_by_variable[name] = xr.DataArray(
                values,
                dims=new_dims,
                coords=new_coords,
                attrs=da.attrs,
                name=name,
            )
    
        # dataset-level coords that don't depend on the reduced dim
        ds_coords = {
            k: v for k, v in ensemble_data.coords.items() if "member" not in v.dims
        }
        ds_coords["percentiles"] = ptileList
        ensPercs= xr.Dataset(percentiles_by_variable, coords=ds_coords, attrs=ensemble_data.attrs)

    # Tidy naming
    ensMean = _renameEnsStats(ensMean, "mean")
    ensSd = _renameEnsStats(ensSd, "standard_deviation")
    ensMax = _renameEnsStats(ensMax, "maximum")
    ensMin = _renameEnsStats(ensMin, "minimum")
    ensPercs = _renameEnsStats(ensPercs, "percentiles")

    # Combine results
    out = xr.merge([ensPercs, ensMean, ensSd, ensN, ensMax, ensMin])

   # Tidy up output-------------------
    # Restore auxiliary coordinates by copying them back into the original dataset.
    # The season mask is the same for all members.
    out["season_mask"] = source_ensemble["season_mask"].isel(member=0)
    # The time bounds can differ between members but have been handled above 
    out["time_bnds"] = source_ensemble["time_bnds"]

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

    print(f"Using {len(input_files)} input files:")
    for i in input_files:
        print(f"\t{i}") 
    print(f"based on requirements for output file:")
    print(f"\t{output_file}")

    # Setup argument list
    argl={"percentiles": [5, 95],
          "method":"midpoint"}
    # Note that this can be expanded into an interactive environment using
    # globals().update(argl)

    out = calculate_ensemble_statistics(input_files=input_files, **argl)
    print("Success!")
