# Given a set of input files, create objects that can be worked with
import xarray as xr
import pandas as pd
from pathlib import Path
import time

# Use absolute imports assuming KAPy is installed
from KAPy import workflow
from KAPy import helpers


def make_variable_overview(config):
    # Get workflow
    wf = workflow.get_workflow(config)

    # Get the list of primaryVar files from the workflow
    wfFiles = [
        g
        for k in wf["primary_variables"].keys()
        for g in wf["primary_variables"][k]["outputs"]
    ]
    tbl = pd.DataFrame(wfFiles, columns=["path"])
    tbl["filename"] = [Path(f).name for f in tbl["path"]]
    tbl["dataset"] = tbl["filename"].str.split("_").str[0]
    tbl["var"] = tbl["filename"].str.split("_").str[1]
    tbl["grid"] = tbl["filename"].str.split("_").str[2]
    tbl["expt"] = tbl["filename"].str.split("_").str[3]
    tbl["ensemble_member"] = tbl["filename"].str.split("_").str[4:].str.join("_")
    tbl["ensemble_member"] = (
        tbl["ensemble_member"].str.removesuffix(".nc").str.removesuffix(".pkl")
    )

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
        thisrw["file_exists"] = Path(thisrw["path"]).exists()
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
                thisrw["frequency"] = xr.infer_freq(dat.time)
                thisrw["start_date"] = min(dat.time.values).strftime("%Y-%m-%d")
                thisrw["end_date"] = max(dat.time.values).strftime("%Y-%m-%d")
                thisrw["time_steps"] = dat.time.size
                thisrw["duplicates"] = dat.time.to_series().duplicated().sum()
                thisrw["time_span_days"] = (
                    max(dat.time.values) - min(dat.time.values)
                ).days
                thisrw["largest_timestep_days"] = dat.time.to_series().diff().max().days
                thisrw["smallest_timestep_days"] = (
                    dat.time.to_series().diff().min().days
                )

        # Store outputs
        outList += [thisrw]

    snakemake_progress(tbl.shape[0], tbl.shape[0], startTime)

    # Output results
    out = pd.DataFrame(outList)
    cols = out.columns.tolist()
    reordered_cols = cols[2:] + cols[:2]
    out = out[reordered_cols]
    out = out.sort_values(by=["var", "dataset", "grid", "expt", "ensemble_member"])
    outFname = helpers.get_OUTPUT_PATHS(config["output_directory"])["variable_overview"]
    print(f"\nWriting output to '{outFname}'.\n")
    out.to_csv(outFname, index=False)

    return out


# Development setup----------------
if __name__ == "__main__":
    # Setup for debugging
    import KAPy

    # Test standard config first
    config = KAPy.get_config("./config/config.yaml")
    out = make_variable_overview(config)
    print("Success!")
