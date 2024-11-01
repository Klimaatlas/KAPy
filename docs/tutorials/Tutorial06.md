# Tutorial 6 - Introducing other bias calibration methods in KAPy

## Goal

To introduce multiple climate model calibration methods in KAPy.

## Point of departure

This tutorial follows on directly from the end of [Tutorial 5](Tutorial05.md).

## Brief introduction on the 

This tutorial is based on three calibration methods from xclim python package. These are:

`Empirical Quantile Mapping (EQM)`:Adjusts data by aligning the quantiles of modeled and observed distributions, allowing for a more tailored correction across the range of data values.

`Detrended Quantile Mapping (DQM)`: Similar to EQM but first removes long-term trends from the modeled data, correcting for biases while preserving climate change signals.

`Scaling`: A simpler method that applies a uniform correction factor (e.g., mean or standard deviation) to align model data with observed averages, primarily addressing systematic biases without altering data distribution.
These methods allow for flexible adjustments depending on the nature and complexity of the biases.

More information on these methods can be found [here](https://xclim.readthedocs.io/en/stable/notebooks/sdba.html) 

## Instructions
1. In the previous tutorials, you performed a complete run of a KAPy pipeline, starting from a fresh installation up to where you introduced a shapefile for areal averaging over a polygon of interest. This configuration only used a single calibration method i.e `xclim scaling` method, to adjust the bias in the models. In some cases, you may want to use multiple bias adjustment methods and compare the results.  Here, we will introduce other calibration methods into KAPy and compare a few results.
   
3. Start by getting an overview of the calibrated files present in the current version of the pipeline. Note in particular that the `./outputs/2.calibration` folder only contains set of files calibrated using the scaling method
```
ls ./outputs/2.calibration/*
```

4. Calibration methods are defined and configured via `./config/calibration.tsv`. Open this file in a text editor (e.g. `vi`) and have a look. Here you will see that the `tas-scaling` and `pr-scaling` are defined in the first two rows, and that they are based on the `xclim-scaling` calibration method defined in the `method` column.  Note also under `additionalArgs` that we are passing `kind='+'` for `calibrationVariable` `tas` to use calibration in the addative mode. Here, the adjustment factors are added/subtracted. For `pr`, the `kind='*'` option is passed instead where djustment factors are multiplied/divided instead of being added/subtracted

5. The reference period used in the calibration is defined by `calPeriodStart` and `calPeriodEnd` while the source of the climate model data and reference data used for calibration are defined under `calibSource` and `refSource`, respectively.
   
6. Now lets add a new calibration method named Empirical Quantile Mapping `xclim-eqm` by replicating the rowns in the table in `./config/calibration.tsv` albeit with only the `method` column changing. Take care to ensure that the tab separators are maintained between each entry. Open `./config/calibration.tsv in your spreadsheet programme and modify it to look like the following. Save the file. If you strike problems, a correctly formated version of this table can be downloaded from [here](Tutorial06_files),

```
id	outVariable	calibrationVariable	calibSource	refSource	calPeriodStart	calPeriodEnd	method	grouping	additionalArgs	customScriptPath	customScriptFunction
tas-scaling  tas-scaling	tas	CORDEX	ERA5	1981	2010	xclim-scaling	month	{'kind':'+'}
pr-scaling  pr-scaling	pr	CORDEX	ERA5	1981	2010	xclim-scaling	month	{'kind':'*'}			
tas-eqm	tas-eqm	tas	CORDEX	ERA5	1981	2010	xclim-eqm	month	{'kind':'+'}		
pr-eqm	pr-eqm	pr	CORDEX	ERA5	1981	2010	xclim-eqm	month	{'kind':'*'}	
```

7. Next, edit the table in ./config/indicators.tsv` file for KAPy to include the new calibration method in the next run. Open the file in a text editor in your spreadsheet programme. Currently, the table is defining the indicators based on the uncalibrated data `101-nocal` and the `xclim-scaling` calibrated data `101-scaling`. Now we add the `xclim-eqm` method. Modify this `./config/indicators.tsv` to look like the following. Save the file. If you strike problems, a correctly formated version of this table can be downloaded from [here](Tutorial06_files),
```
id	name	units	variables	season	statistic	time_binning
101-nocal	Annual mean temperature	K	tas	annual	mean	years
102-nocal	Annual mean precipitation	kg m-2 s-1	pr	annual	mean	years
101-scaling	Annual mean temperature	K	tas-scaling	annual	mean	years
102-scaling	Annual mean precipitation	kg m-2 s-1	pr-scaling	annual	mean	years
101-eqm	Annual mean temperature	K	tas-eqm	annual	mean	years
102-eqm	Annual mean precipitation	kg m-2 s-1	pr-eqm	annual	mean	years
```
8. So now we are ready to go. Firstly, let's see how snakemake responds to this new configuration.
```
snakemake -n
```
9. We can see that Snakemake wants to run the new rule for hgeeting `101-eqm` files, corresponding to the new output files. Run the code to add another set of files calibrated using the `xclim-eqm` method
```
snakemake --cores 1
```
12. Once the output has been completed, a can see new set of files e.g 
```
ls ./outputs/2.calibration/*
```

13. Output plots for 102 are also generated automatically. Try browsing the plots in a viewer e.g
```
eog ./outputs/7.plots/*
```

14. To add a new calibration method Detrended Quantile Mapping `xclim-dqm` to the KAPy pipeline, follow the steps `6` to `12` albeit using `eqm` with `dqm`.


15. Do a small comparison of the outputs derived from data calibrated by the different methods. An example of how can do this is by using the small Python code below:


16. That concludes this tutorial. KAPy is currently  limited to these three calibratiopn methods, but within a short time, more methods will be added.
