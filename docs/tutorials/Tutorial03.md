# Tutorial 3 - Adding a new indicator

## Goal

To learn how indicators are configured in KAPy.

## Point of departure

This tutorial follows on directly from the end of [Tutorial 1](Tutorial01.md).

## Instructions

1. In Tutorial 1, you performed a complete run of a KAPy pipeline, starting from a fresh installation. This configuration calculated a single indicator, an average over 30-year periods. Here we will add a second indicator to the configuration and rerun the analysis.

2. Start by getting an overview of the files present in the current version of the pipeline. Note in particular that the `indicators` folder only contains one set of indicators, `i101_`
```
ls ./workDir/*
```

3. Indicators are defined and configured via `config.yaml`. Open this file in a text editor (e.g. `vi`) and have a look at the indicators section. Here you will see where `i101` is defined, and that it is based on time-binning over `periods`.

4. Modify the indicator section to look like the following and save the file. Take particular care to ensure that the indenting is maintained correctly, as this is a critical aspect of how Python (and therefore) KAPy reads the configuration file. `i102` is a direct copy of `i101`, but with annual time resolution rather than binning over periods.
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
```

5. So now we are ready to go. Firstly, let's see how snakemake responds to this new configuration.
```
snakemake -n

```

6. We can see that Snakemake wants to run the new rule `i102_file` six times, corresponding to the new output files. Note that `i101` is however not being run, as it has already been run in previous tutorials - again, Snakemake is lazy and smart, and only does what is necessary.

7. We can also review the revised DAG with `i102` incorporated. Open the file `dag_tutorial03.png` and compare it to the previously created DAG - you will see the addition of the `i102`files, but that they are also derived from the same input files. Note also the borders around each file - a dashed line means that the file does not need to be rerun, whereas a solid line means that the file either doesn't exist or needs to be recreated to reflect the updates.

```
snakemake notebooks --dag | dot -Tpng -Grankdir=LR > dag_tutorial03.png
```

8. So, let's do it.

```
snakemake --cores 1

```

9. Once the output has been completed, start by having a look at the `arealstats` files. Comparing `i101` and `i102`you will see the difference in the time resolution straight away.
```
head workDir/7.areal_statistics/i101_CORDEX_rcp85_ensstats.csv 
head workDir/7.areal_statistics/i102_CORDEX_rcp85_ensstats.csv 
```

10. `i102` is also added automatically to the output notebook. Try opening it in a browser e.g. Firefox.

```
firefox workDir/notebooks/Output_overview.py.html 
```

11. That concludes this tutorial KAPy is currently only limited to calculating means over a time window, but within a short time, more functions will be added, including the ability to define custom functions.

