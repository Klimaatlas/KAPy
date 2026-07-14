# Given a set of input files, create objects that can be worked with
import xarray as xr
import time
from cdo import Cdo
import numpy as np
import xclim
import pandas as pd
import glob
import os
from . import helpers
from . import workflow
from .constants import CHUNKING_TIME


# -----------------------------------------------------------------
def default_import(
    input_files,
    variable_code,
    internal_variable_name,
    checks,
    chunks={"time": CHUNKING_TIME},
):
    # Make dataset object using xarray lazy load approach.
    #
    # Setup
    time_coder = xr.coders.CFDatetimeCoder(use_cftime=True)
    try:
        dsIn = xr.open_mfdataset(
            input_files,
            combine="by_coords" if checks == "all" else "nested",
            concat_dim=None if checks == "all" else "time",
            decode_times=time_coder,
            join="exact" if checks == "all" else "override",
            compat="no_conflicts" if checks == "all" else "override",
            coords="minimal",
            data_vars="minimal",
            chunks=chunks,
            preprocess=lambda ds: ds[[internal_variable_name]],
        )

    except Exception as e:
        raise RuntimeError(
            f"Opening following NetCDF files:\n '{input_files}'\n failed with error:\n{e}"
        )

    # Select the desired variable to give a and rename to the variable code
    da = dsIn[internal_variable_name]
    da.name = variable_code

    # Drop degenerate dimensions. If any remain, throw an error
    da = da.squeeze(drop=True)
    if len(da.dims) != 3:
        raise ImportError(
            "Extra dimensions found during import - there should be only "
            + "three dimensions after degenerate dimensions are dropped but "
            + f"found {len(da.dims)} i.e. {da.dims}."
        )

    # Drop coordinates that are not associated with a dimension. Often you seen
    # height or level coming in as a coordinate, when it is perhaps more appropriate as
    # an attribute. However, different models handle this differently, and some have
    # already dropped it. The different between the two can cause problems when we
    # come to the point of merging ensemble members.
    for thisCoord in da.coords.keys():
        if len(da[thisCoord].dims) == 0:
            da.attrs[thisCoord] = da[thisCoord].values
            da = da.drop_vars(thisCoord)

    return da


# -----------------------------------------------------------------
def cutout_lonlat(thisDat, xmin, xmax, ymin, ymax, variable_code, **kwargs):
    """
    Apply cutout based on lonlat

    The processing chain here is to first take
    a single timeframe, and then use cdo sellonlat to perform at cutout on it. This
    is then used as a mask across the full the xarray object - this way we can
    maintain the lazy-loading and storage benefits associated with pickling, without
    having to get our hands too dirty about dealing with unusual coordinate systems.

    Parameters
    ----------
    xmin : _type_
            Minimum coordinate in the x direction
    xmax : _type_
            Maximum coordinate in the x dirction
    ymin : _type_
            Minimum coordinate in the y direction
    ymax : _type_
            Maximum coordinate in the y direction
    variable_code : _type_
            Name of the variable ID contained in the dataset
    kwargs:
            Absorb any extra arguments
    """
    # Extract first time step. This avoids having to work
    # with the entire dataset.
    # ASSERT: there is a time dimension called "time"
    if "time" not in thisDat.dims:
        raise ValueError("DataArray must contain a 'time' dimension")
    firstTS = thisDat.isel(time=0)

    # Create a mask as the basis for the cutouts using cdo masklonlatbox.
    # Make sure that we return a dataarray and not a dataset by specifying the
    # variable_code
    cdo = Cdo()
    mask = cdo.masklonlatbox(
        xmin, xmax, ymin, ymax, input=firstTS, returnXArray=variable_code
    )

    # Find the intersection of the two
    da = thisDat.where(mask.notnull(), drop=True)

    # Done
    return da


# -----------------------------------------------------------------
def build_primary_variable(
    input_files,
    variable_code,
    internal_variable_name,
    checks,
    custom_script,
    custom_function,
    units,
    cutoutArgs,
    **kwargs,
):
    # If an import function is defined, use that. Otherwise use the default
    if custom_script == "":
        # Use default import
        da = default_import(
            input_files=input_files,
            variable_code=variable_code,
            internal_variable_name=internal_variable_name,
            checks=checks,
        )
        # Apply cutout functionality
        if cutoutArgs["method"] == "lonlatbox":
            da = cutout_lonlat(da, **cutoutArgs, variable_code=variable_code)

    else:
        # Use a custom import
        imptFn = helpers.get_external_function(custom_script, custom_function)
        da = imptFn(
            input_files,
            variable_code=variable_code,
            internal_variable_name=internal_variable_name,
            units=units,
            checks=checks,
            cutoutArgs=cutoutArgs,
        )

    # Unit handling -----------------------------
    # Note that this is enforced here, even if it is already handled in the custom
    # configuration. There are three separate cases we need to handle

    # Case 1 - no units attribute on da:
    # => Set units directly but fail if not specified
    if "units" not in da.attrs:
        if units == "":
            raise ValueError(
                "Units argument is blank but needs to be supplied in cases where there are no units in the input file."
            )
        else:
            da.attrs["units"] = units

    # Case 2 - da has units, but argument is null:
    # => leave as in

    # Case 3 - da has units, argument is specified
    # => Convert units of data to specified
    elif not units == "":
        da = xclim.core.units.convert_units_to(da, units)

    # Check that the unit choice is sane

    # Checks -----------------------------------------
    # We need to do some checks on at least the time dimension
    if not da.indexes["time"].is_monotonic_increasing:
        raise ValueError(
            f"Time coordinate is not monotonic in file set: '{input_files}'."
        )
    if da.indexes["time"].has_duplicates:
        raise ValueError(f"Duplicate timestamps detected file set: '{input_files}'.")

    # Output --------------------
    # We also apply a little trick here, by forcing everything to be stored as
    # netcdf "float" types as well.
    daFloat = da.astype(np.float32)

    return daFloat


def make_variable_overview(config):
    # Get workflow
    wf = workflow.get_workflow(config)

    # Get the list of primaryVar files from the workflow and
    # complement with directory search of existing files.
    # TODO:
    #  - Remove duplicates
    #  - Split fname into fields
    #  - Calculate differences
    wfFiles = [g for k in wf["primVars"].keys() for g in wf["primVars"][k]]
    ncFiles = glob.glob(config["dirs"]["variables"] + "/**/*.nc", recursive=True)
    tbl = pd.DataFrame(sorted(set(wfFiles + ncFiles)), columns=["path"])
    tbl["filename"] = [os.path.basename(f) for f in tbl["path"]]
    tbl["var"] = tbl["filename"].str.extract("^([^_]+)_.*$")
    tbl["dataset"] = tbl["filename"].str.extract("^[^_]+_([^_]+)_.*$")
    tbl["grid"] = tbl["filename"].str.extract("^[^_]+_[^_]+_([^_]+)_.*$")
    tbl["expt"] = tbl["filename"].str.extract("^[^_]+_[^_]+_[^_]+_([^_.]+).*$")
    tbl["ensemble_member"] = tbl["filename"].str.extract(
        "^[^_]+_[^_]+_[^_]+_[^_]+_(.+).nc(?:.pkl)?$"
    )
    tbl["in_workflow"] = [f in wfFiles for f in tbl["path"]]

    # ChatGPT made this nice little progress bar for us
    def snakemake_progress(i, total, start_time, prefix="", length=40):
        elapsed = time.time() - start_time
        percent = (i / total) * 100
        filled_length = int(length * i // total)
        bar = "█" * filled_length + "-" * (length - filled_length)

        # Estimate remaining time
        eta = (elapsed / i) * (total - i) if i > 0 else 0
        eta_str = time.strftime("%H:%M:%S", time.gmtime(eta))

        print(f"\r{prefix} |{bar}| {percent:6.2f}% ETA: {eta_str}", end="", flush=True)
        if i == total:
            print()

    # Now loop over the files
    outList = []
    startTime = time.time()
    print(f"Processing {tbl.shape[0]} files...")
    for thisidx, thisrw in tbl.iterrows():
        # Basic progress bar
        snakemake_progress(thisidx, tbl.shape[0], startTime)

        # Check that object exists
        thisrw["file_exists"] = os.path.exists(thisrw["path"])
        # If the file exists, load it
        if thisrw["file_exists"]:
            # Try to load the file
            try:
                dat = helpers.read_file(thisrw["path"])
                thisrw["loadsOK"] = True
            except Exception:
                thisrw["loadsOK"] = False

            # Extract useful info if possible
            if thisrw["loadsOK"]:
                thisrw["calendar"] = dat.time.values[0].calendar
                thisrw["start_date"] = min(dat.time.values).strftime("%Y-%m-%d")
                thisrw["end_date"] = max(dat.time.values).strftime("%Y-%m-%d")
                thisrw["time_span"] = (max(dat.time.values) - min(dat.time.values)).days
                thisrw["time_points"] = dat.time.size
                thisrw["gaps"] = thisrw["time_points"] - thisrw["time_span"] - 1

        # Store outputs
        outList += [thisrw]

    # Output results
    out = pd.DataFrame(outList)
    cols = out.columns.tolist()
    reordered_cols = cols[2:] + cols[:2]
    out = out[reordered_cols]
    out = out.sort_values(by=["var", "dataset", "grid", "expt", "ensemble_member"])
    outFname = os.path.join(config["dirs"]["variables"], "Variable_overview.csv")
    print(f"\nWriting output to '{outFname}'.\n")
    out.to_csv(outFname, index=False)


# Validation----------------
if __name__ == "__main__":
    # Setup for debugging
    from pathlib import Path

    pd.set_option("display.max_colwidth", None)
    from config import get_config

    # Setup working directory. Its not pretty, but..
    this_path = Path(__file__).resolve().parent.parent.parent
    os.chdir(this_path)

    # Test standard config first
    config = get_config("./config/config.yaml")

    # Then test the testing config
    config = get_config("./workflow/testing/config.yaml")

"""
#Setup for debugging with VSCode
import os
print(os.getcwd())
os.chdir("KAPy/workflow")
import KAPy
os.chdir("../..")
print(os.getcwd())
config=KAPy.get_config("./config/config.yaml")  
wf=KAPy.get_workflow(config)
inpID=list(wf['primVars'].keys())[0]
output_file=list(wf['primVars'][inpID])[0]
input_files=wf['primVars'][inpID][output_file]
import KAPy.helpers as helpers
import KAPy.workflow as workflow
%matplotlib inline
"""
