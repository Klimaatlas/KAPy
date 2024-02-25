# Tutorial 4 - Adding a new datasource

## Goal

To learn how new input data sources are configured in KAPy.

## Point of departure

This tutorial follows on directly from the end of [Tutorial 1](Tutorial01.md).

## Instructions

1. In Tutorial 1, you performed a complete run of a KAPy pipeline, starting from a fresh installation. This configuration only used a single data source (CORDEX tas) whereas in a real setting we will want to work with more than that. Here we will add precipitation to the original tas dataset, and then define new indicators to exploit it.

2. First, we need to get some more data. Precipitation data for the same Ghana domain is available from https://download.dmi.dk/Research_Projects/KAPy/pr_example_dataset.zip. Download the file into a temporary directory, unzip it, and copy the contents into `./workDir/1.inputs` as before. Check the contents of this directory - you should see files starting with both `tas_*`and `pr_*` now.

```
ls workDir/1.inputs/CORDEX/*
```

3. Input data sources are defined via the `inputs` tag in `config.yaml`. Open this file in a text editor (e.g. `vi`) and have a look at the input data section. It should be clear where tas is defined.

4. Next, we need to modify this section to incorporate the new data inputs. Make the following changes, taking care to maintain the indenting, and save the file.

```
inputs:  #Define list of input data sources
    CORDEX: 
        tas:
            path: "CORDEX/tas_*"   #Glob
            regex: "^tas_(.*)_.*?.nc$" # Brackets are the common element 
            internalVarName: "tas"
        pr:
            path: "CORDEX/pr_*"   #Glob
            regex: "^pr_(.*)_.*?.nc$" # Brackets are the common element 
            internalVarName: "pr"
    ERA5:
        tas:
            path: "ERA5_monthly/t2m_ERA5_monthly.nc"
            regex: "^t2m_(.*).nc$"  
            internalVarName: "t2m"
        pr:
            path: "ERA5_monthly/pr_ERA5_monthly.nc"
            regex: "^pr_(.*).nc$"  
            internalVarName: "tp"
```

5. Note the addition of the new `pr` tags to the `CORDEX` and `ERA5` inputs. `path` is the path to the files, including a `*` glob to allow for general pattern matching. `regex` is a regular expression used to describe the structure of the filenames - the bracketed section are the common elements in the filename. `internalVarName` is the internal representation of the variable - in this case, ERA5 calls precipitation `tp` rather than `pr` in CORDEX.

6. We also want to do something with this input dataset, so we need to define some indicators that can use it as well. Modify the indicator section of `config.yaml` to look like the following and save the file, maintaining indenting. Here we have added two parallel indicators to `i101` and `i102` that work with `pr` rather than `tas`. 
```
indicators:
    101:
        id: 101
        name: 'Annual mean temperature'
        units: 'K'
        variables: 'tas'
        season: 'Annual'   #Use key name for seasons. Use 'All' for all defined seasons.
        statistic: 'mean'
        time_binning: "periods" #Choose between periods, years, months
    102:
        id: 102
        name: 'Annual mean temperature'
        units: 'K'
        variables: 'tas'
        season: 'Annual'   #Use key name for seasons. Use 'All' for all defined seasons.
        statistic: 'mean'
        time_binning: "years" #Choose between periods, years, months
    201:
        id: 201
        name: 'Annual mean precipitation'
        units: 'kg m-2 s-1'
        variables: 'pr'
        season: 'Annual'   #Use key name for seasons. Use 'All' for all defined seasons.
        statistic: 'mean'
        time_binning: "periods" #Choose between periods, years, months
    202:
        id: 202
        name: 'Annual mean precipitation'
        units: 'kg m-2 s-1'
        variables: 'pr'
        season: 'Annual'   #Use key name for seasons. Use 'All' for all defined seasons.
        statistic: 'mean'
        time_binning: "years" #Choose between periods, years, months
```

6. So now we are ready to go. Firstly, lets see how snakemake responds to this new configuration - lots of new things to do.
```
snakemake -n

```

7. The revised DAG is also more complicated as a result. Open the file `dag_tutorial04.png` and compare it to the previous DAGs.

```
snakemake notebooks --dag | dot -Tpng -Grankdir=LR > dag_tutorial04.png
```

8. Make it so!

```
snakemake --cores 1

```

9.  The difference will be most apparent in the output notebook. Try opening it in a browser e.g. Firefox.

```
firefox workDir/notebooks/Output_overview.py.html 
```

10. That concludes this tutorial. KAPy is designed to handle multiple different data sources within the same framework. For example, applying the same processing chains to data from ERA5, CMIP5, and CMIP6 will all be possible within the same workflow in the future.

