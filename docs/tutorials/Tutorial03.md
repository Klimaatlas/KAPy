# Tutorial 3 - Adding a new indicator

## Goal

To learn how indicators are configured in KAPy.

## What are we going to do?

In this tutorial we will define a new indicator and rerun the KAPy pipeline to get a second set of results. The second indicator is the annual average temperature in each year, as in Tutorials 1 and 2, is calculated for both two emissions scenarios from CORDEX and from ERA5 data over Ghana.


## Point of departure

This tutorial follows on directly from the end of [Tutorial 1](Tutorial01.md).

## Instructions

1. In Tutorial 1, you performed a complete run of a KAPy pipeline, starting from a fresh installation. This configuration calculated a single indicator, an average over 30-year periods. Here we will add a second indicator to the configuration and rerun the analysis.

2. Start by getting an overview of the files present in the current version of the pipeline. Note in particular that the `./outputs/3.indicators` folder only contains one set of indicators, `101`
```
ls ./outputs/3.indicators/*
```

3. Indicators are defined and configured via `./config/indicators.tsv`. Open this file in a spreadsheet (e.g. LibreOffice) and have a look at the indicators section. Here you will see that indicator `101` is defined as the first row, and that it is based on time-binning over `periods`. 

4. The periods are defined in `./config/periods.tsv`. Open this file and you will see that they are declared as consecutive 30 year blocks with a start-year and end-year.

4. Now lets add a new indicator. The configuration tables are defined as tables in the `.tsv` (tab-separated variables) format. They can be edited using a text editor, if you take care to ensure that the tab separators are maintained between each entry. However, a more robust and recommended way to do it is to edit it via a spreadsheet programme, such as LibreOffice or Excel. Open `./config/indicators.tsv` in your spreadsheet programme and modify it to look like the following. Save the file. In this new configuration indicator `102` is a direct copy of `101`, but with annual time resolution rather than binning over periods. If you strike problems, a correctly formated version of this table can be downloaded from [here](Tutorial03_files/indicators.tsv).

```
id	name	units	variables	season	statistic	time_binning
101	Annual mean temperature	K	tas	annual	mean	periods
102	Annual mean temperature	K	tas	annual	mean	years
```

5. So now we are ready to go. Firstly, let's see how snakemake responds to this new configuration.
```
snakemake -n
```

6. We can see that Snakemake wants to run the new rule `indicator_102_file` six times, corresponding to the new output files. Note that `indicator_101_file` is however not being run, as it has already been run in previous tutorials - again, Snakemake is lazy and smart, and only does what is necessary.

7. We can also review the revised DAG with indicator `102` incorporated. Open the file `dag_tutorial03.png` and compare it to the previously created DAG - you will see the addition of the `102_*`files, but that they are also derived from the same input files. Note also the borders around each file - a dashed line means that the file does not need to be rerun, whereas a solid line means that the file either doesn't exist or needs to be recreated to reflect the updates.

```
snakemake --dag | dot -Tpng -Grankdir=LR > dag_tutorial03.png
```

8. Make it so.

```
snakemake --cores 1

```

9. Once the output has been completed, start by having a look at the `arealstats` files. Comparing `101` and `102`you will see the difference in the time resolution straight away.
```
head outputs/6.areal_statistics/ensstats/101_CORDEX_Ghana025_rcp26_ensstats.csv 
head outputs/6.areal_statistics/ensstats/102_CORDEX_Ghana025_rcp26_ensstats.csv 
```

10. Output plots for `102` are also generated automatically. Try browsing the plots in a viewer e.g. 

```
eog ./outputs/7.plots/
```

11. That concludes this tutorial. KAPy is currently only limited to calculating means, but within a short time, more functions will be added, including the ability to define custom functions.

