# Tutorial 6 - Addition of calibration methods

## Goal

To implement calibration methods in KAPy.

## What are we going to do?

In this tutorial we implement a bias-correction method in KAPy. We use the simulated monthly temperature from CORDEX over Ghana for two emissions scenarios, and correct against ERA5 as the observational reference dataset.

## Point of departure

This tutorial follows on directly from the end of [Tutorial 01](Tutorial01.md).

## Background 

This tutorial performs bias-correction using the `scaling` approach from the `xclim python` package. This is a simpler method that applies a uniform correction factor (e.g., mean or standard deviation) to align model data with observed averages, primarily addressing systematic biases without altering data distribution. More information on the method can be found [here](https://xclim.readthedocs.io/en/stable/notebooks/sdba.html) 

## Instructions
1. In the previous tutorials, you performed a complete run of a KAPy pipeline without calibration methods turned on. Calibration functionality is enabled first in `config/config.yaml` in the `configurationTables` section. Start by commenting the option for `calibration` back in:

```
configurationTables:
    inputs:  'config/inputs.tsv'
    indicators: 'config/indicators.tsv'
    calibration: 'config/calibration.tsv'
    periods:  'config/periods.tsv'
    seasons: 'config/seasons.tsv'
```

2. The calibration methods are defined and configured via `./config/calibration.tsv` which is already available and configured correctly in a default install of KAPy. Open this file in a spreadsheet (e.g. LibreOffice) and have a look. Here you will see that the definition of a calibrated variable called `tas-cal`. This  output variable is based on using `tas` from `CORDEX` as the datasource, and is calibrated against `ERA5` as the reference source, using the period 1981-2010 as the reference. The calibration method is set in the `method`column to `xclim-scaling`, while the `grouping` argument is set to `month`, indicating that we should perform the calibration individually on months.  Note also under `additionalArgs` that we are passing a dict with `kind='+'` to use calibration in the additive mode - this is appropriate for temperature, but a multiplicative model `kind= '*'` would be more appropriate for precipitation. 

3. Next, we want to be able to use the new variable that we have created, `tas-cal` in generating indicators. A new indicator table can be downloaded from [here](Tutorial06_files/indicators.tsv). Save the file over the top of the old  indicator table `./config/indicators.tsv`, then open the file using a spreadsheet. The table includes the definition of two indicators: `101-nocal` is the annual average of the raw model output temperature `tas`, while `101-scaling` is the annual average of the same data after calibration (as stored in the `tas-cal` variable). 

4. So now we are ready to go. Firstly, let's see how snakemake responds to this new configuration.
```
snakemake -n

```
5. We get a list of what Snakemake wants to do - in particular note the generation of the two versions of indicator 101. Now run the pipeline:
```
snakemake --cores 1
```

6. Once the output has been completed, you can see the new set of calibrated variables have appeared in the `calibration`directory  e.g.,
```
ls ./outputs/2.calibration/*
```

7. Output plots for 102 are also generated automatically. Try browsing the plots in a viewer e.g
```
eog ./outputs/7.plots/*
```

8. Do a quick comparison of the outputs derived with and without calibration. In `101-scaling` you will see that the CORDEX values in `101-nocal` have been moved to align with the ERA5 values e.g. the mean values for CORDEX rcp85 in 1950 are arond 298K in `101-nocal` but have been shifted to around 300 K in `101-scaling`.

9. You can perform a more detailed analysis on your own using e.g. `Python`, `R` or your programming language of choice. We have included a Python example, that can be downloaded from [here](Tutorial06_files/compare_calibration.py). You can run the script as follows:
```
python docs/tutorials/Tutorial06_files/compare_calibration.py
```
10. The script writes an output figure `Tutorial06.png` to the KAPy root directory. Opening if with an image viewer, you will see the shift in the mean temperature between the `nocal` and `scaling` indicators more clearly (in this case for the RCP8.5) scenario. Note also the close agreement between ERA5 and `CORDEX-101-scaling` during the calibration period 1981-2010.

11. That concludes this tutorial. KAPy is currently  limited to these three calibratiopn methods, but within a short time, more methods will be added.
