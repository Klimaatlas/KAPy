# Plotting functions to be used in notebooks
"""
#Debugging setup for VS Code
import os
print(os.getcwd())
os.chdir("..")
import KAPy
os.chdir("..")
config=KAPy.getConfig("./config/config.yaml")  
wf=KAPy.getWorkflow(config)
"""

from plotnine import *
import pandas as pd
import os
import xarray as xr
import matplotlib

# Set default backend to workaround problems caused by the
# default not being uniform across systems - in particular, we 
# hit a problem with micromamba vs conda having different defaults.
# This lead to a crashes when running in a non-Gui environment
matplotlib.use('Agg')

# Boxplot---------------------------------------------------------------------------
"""
indID="101"
srcFiles=list(wf['plots'].values())[0]
srcFiles=['results/5.areal_statistics/101_CORDEX_Ghana025_rcp26_ensstats.csv',
          'results/5.areal_statistics/101_CORDEX_Ghana025_rcp85_ensstats.csv']
"""

def makeBoxplot(config, indID, srcFiles, outFile=None):
    # Extract indicator info
    thisInd = config["indicators"][indID]

    # Load csv files as panadas dataframes
    # Note that we need to make sure that we read the ID's as strings
    dat = []
    for f in srcFiles:
        datIn = pd.read_csv(f)
        datIn["fname"] = os.path.basename(f)
        datIn["periodID"] = [str(x) for x in datIn["periodID"]]
        datIn["experiment"] = datIn["fname"].str.extract("^[^_]+_[^_]+_[^_]+_([^_]+)_.*$")
        dat += [datIn]
    datdf = pd.concat(dat)

    # Get metafra data from configuration
    ptileTbl = (
        pd.DataFrame.from_dict(
            config["ensembles"], orient="index", columns=["percentiles"]
        )
        .reset_index()
        .rename(columns={"index": "ptileLbl"})
    )
    periodTbl = pd.DataFrame.from_dict(config["periods"], orient="index")
    periodLblDict = {
        x["id"]: f"{x['name']}\n({x['start']}-{x['end']})"
        for i, x in periodTbl.iterrows()
    }

    # Now merge into dataframe and pivot for plotting
    pltLong = pd.merge(datdf, ptileTbl, on="percentiles", how="left")
    pltDatWide = pltLong.pivot_table(
        index=["experiment", "periodID"], columns="ptileLbl", values="mean"
    ).reset_index()

    # Now plot
    p = (
        ggplot(pltDatWide)
        + geom_boxplot(
            mapping=aes(
                x="periodID",
                fill="experiment",
                middle="centralPercentile",
                ymin="lowerPercentile",
                ymax="upperPercentile",
                lower="lowerPercentile",
                upper="upperPercentile",
            ),
            width=0.5,
            stat="identity",
        )
        + labs(
            x="Period",
            y=f"Value ({thisInd['units']})",
            title=f"{thisInd['name']} ",
            fill="Experiment",
        )
        + scale_x_discrete(labels=periodLblDict)
        + theme_bw()
        + theme(legend_position="bottom", panel_grid_major_x=element_blank())
    )

    # Output
    if outFile is not None:
        p.save(outFile[0],
               verbose=False)
    return p


# Spatialplot -----------------------------------------------------------
"""
indID='101'
srcFiles=list(wf['plots'].values())[1]
"""
def makeSpatialplot(config, indID, srcFiles, outFile=None):
    # Extract indicator info
    thisInd = config["indicators"][indID]

    # Read netcdf files using xarray and calculate difference
    datdf = []
    for d in srcFiles:
        # Import object
        thisdat = xr.open_dataset(d)
        # We want to plot a spatial map of the first and last indicators
        firstlast = thisdat.isel(periodID=[0,-1])
        firstlastdf = firstlast.indicator_mean.to_dataframe().reset_index()
        firstlastdf["fname"] = os.path.basename(d)
        firstlastdf["experiment"] = firstlastdf["fname"].str.extract("^[^_]+_[^_]+_[^_]+_([^_]+)_.*$")
        datdf += [firstlastdf]
    pltDat = pd.concat(datdf)

    #Identify spatial coordinates
    spDimX=[d for d in pltDat.columns if d in ['x','longitude','long']]
    spDimY=[d for d in pltDat.columns if d in ['y','latitude','lat']]
    pltDat['x']=pltDat[spDimX]
    pltDat['y']=pltDat[spDimY]

    # Make plot
    p = (
        ggplot(pltDat, aes(x="x", y="y", fill="indicator_mean"))
        + geom_raster()
        + facet_grid("periodID~experiment")
        + theme_bw()
        + labs(
            x="",
            y="",
            fill=f"Value\n({thisInd['units']})",
            title=f"{thisInd['name']} "
        )
        + scale_x_continuous(expand=[0, 0])
        + scale_y_continuous(expand=[0, 0])
        + theme(legend_position="bottom")
        + coord_fixed()
    )

    # Output
    if outFile is not None:
        p.save(outFile[0],
               verbose=False)
    return p


# Lineplot------------------------------------------------------------------
"""
indID=101
srcFiles=list(wf['plots'].values())[0]
"""


def makeLineplot(config, indID, srcFiles, outFile=None):
    # Extract indicator info
    thisInd = config["indicators"][indID]

    # Load csv files as panadas dataframes
    dat = []
    for f in srcFiles:
        datIn = pd.read_csv(f)
        datIn["fname"] = os.path.basename(f)
        datIn["experiment"] = datIn["fname"].str.extract("^[^_]+_[^_]+_[^_]+_([^_]+)_.*$")
        dat += [datIn]
    datdf = pd.concat(dat)
    datdf["datetime"] = pd.to_datetime(datdf["time"])

    # Now select data for plotting - we only plot the central value, not the full range
    pltDat = datdf[datdf["percentiles"] == config["ensembles"]["centralPercentile"]]

    # Now plot
    p = (
        ggplot(pltDat, aes(x="datetime", y="mean", colour="experiment"))
        + geom_line()
        + labs(
            x="",
            y=f"Value ({thisInd['units']})",
            title=f"{thisInd['name']} ",
            colour="Scenario",
        )
        + theme_bw()
        + theme(legend_position="bottom")
    )
    # Output
    if outFile is not None:
        p.save(outFile[0],
               verbose=False)
    return p
