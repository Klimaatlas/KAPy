# Tutorial 4 - Adding a new data source

## Goal

To learn how new input data sources are configured in KAPy.

## Point of departure

This tutorial follows on directly from the end of [Tutorial 1](Tutorial01.md).

## Instructions

1. In Tutorial 1, you performed a complete run of a KAPy pipeline, starting from a fresh installation. This configuration only used a single data source (CORDEX tas) whereas, in a real setting, we will want to work with more than that. Here we will add precipitation to the original tas dataset, and then define new indicators to exploit it.

2. First, we need to get some more data. Download the [precipitation data](https://download.dmi.dk/Research_Projects/KAPy/pr_example_dataset.zip) for the same Ghana domain into a temporary directory, unzip it, and copy the contents into `./resources` as before. Check the contents of this directory - you should see files starting with both `tas_*`and `pr_*` now.

```
ls resources/CORDEX/*
```

3. Input data sources are defined via the input configuration table `./config/inputs.tsv`. Open this file in a text editor (e.g. `vi`). Each row corresponds to an input file type. You should be able to identify one row for CORDEX tas inputs and one for ERA5 inputs.

4. Next, we need to modify this file to incorporate the new data inputs using a `spreadsheet`. For convinience, a correctly formatted version of this file can be found [here](Tutorial04_files) - download and save it over the top of the existing `./config/inputs.tsv`. 

5. Open the new file in a text viewer - you will see that three more lines have been added for precipitation data at the bottom. Note also the addition of the new `pr` tags to the `CORDEX` and `ERA5` inputs. `path` is the path to the files, including a `*` glob to allow for general pattern matching. To allow an intuitive way of uniquely selecting all the input files of interest, certain parts of the original CORDEX file naming structure, separated by the `fieldSeparator` (_), are assigned positions specified in `ensMemberFields`. This method offers a flexible way to generate meaningful criteria for selecting/naming `CORDEX` data files based on a structured naming convention. `internalVarName` is the internal representation of the variable - in this case, ERA5 calls precipitation `tp` rather than `pr` in CORDEX.

6. We also want to do something with this input dataset, so we need to define some indicators that can use it as well. Modify the indicator section of `config.yaml` to look like the following and save the file, maintaining indenting is very important. Here we have added two parallel indicators to `101` and `102` that work with `pr` rather than `tas`. Alternatively you can download a correctly formatted version of this file from [here](Tutorial04_files).

```
id      name    units   variables       season  statistic       time_binning
101     Annual mean temperature K       tas     annual  mean    periods
102     Annual mean temperature K       tas     annual  mean    years
201     Annual mean precipitation       kg m-2 s-1      pr      annual  mean    periods
202     Annual mean precipitation       kg m-2 s-1      pr      annual  mean    years
```

6. So now we are ready to go. Firstly, let's see how snakemake responds to this new configuration - lots of new things to do.
```
snakemake -n

```

7. The revised DAG is also more complicated as a result. Open the file `dag_tutorial04.png` and compare it to the previous DAGs.

```
snakemake --dag | dot -Tpng -Grankdir=LR > dag_tutorial04.png
```

8. Make it so!

```
snakemake --cores 1

```

9.  The difference will be most apparent in the output files. Try browsing through them now in a graphics viewer e.g.

```
eog ./results/6.plots/
```

10. That concludes this tutorial. KAPy is designed to handle multiple different data sources within the same framework. For example, applying the same processing chains to data from ERA5, CMIP5, and CMIP6 will all be possible within the same workflow in the future.

