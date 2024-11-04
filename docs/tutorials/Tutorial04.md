# Tutorial 4 - Adding a new data source

## Goal

To learn how new input data sources are configured in `KAPy`.

## What are we going to do?

In this tutorial we will add two new data sources in the form of precipitation data, again from CORDEX and ERA5. We will then add indicators to build on utilise these new datasets, in the form of annual and 30-year period averages.

## Point of departure

This tutorial follows on directly from the end of [Tutorial 1](Tutorial01.md).

## Instructions

1. In Tutorial 1, you performed a complete run of a `KAPy` pipeline, starting from a fresh installation. This configuration only used data from a single climate variable (`tas`) whereas, in a real setting, we will want to work with more than that. Here we will add precipitation to the original tas dataset, and then define new indicators to exploit it.

2. First, we need to get some more data. Download the [precipitation data](https://download.dmi.dk/Research_Projects/KAPy/pr_example_dataset.zip) for the same Ghana domain into a temporary directory, copy the .zip file into `./inputs/` and unzip it as before. Check the contents of this directory - you should see files starting with both `tas_*`and `pr_*` now.

```
ls inputs/*
```

3. Input data sources are defined via the input configuration table `./config/inputs.tsv`. Open this file in a spreadsheet (e.g. LibreOffice). Each row corresponds to an input file type. You should be able to identify one row for the existing CORDEX tas inputs and one for ERA5 inputs.

4. Next, we need to modify this file to incorporate the new data inputs using a spreadsheet.  A correctly formatted version of this file can be found [here](Tutorial04_files/inputs.tsv) - download and save it over the top of the existing `./config/inputs.tsv`. 

5. Open the new file in a spreadsheet - you will see that two more lines have been added for precipitation data at the bottom. Note also the addition of the new `pr` tags to the `CORDEX` and `ERA5` inputs. `path` is the path to the files, including a `*` glob to allow for general pattern matching. To allow an intuitive way of uniquely selecting all the input files of interest, certain parts of the original CORDEX file naming structure, separated by the `fieldSeparator` (`_`), are assigned positions specified in `ensMemberFields`. This method offers a flexible way to generate meaningful criteria for selecting/naming CORDEX data files based on a structured naming convention. `internalVarName` is the internal representation of the variable - in this case, ERA5 calls precipitation `tp` rather than `pr` in CORDEX.

6. We also want to do something with this input dataset, so we need to define some indicators that can use it as well. Download [this indicator configuration file](Tutorial04_files/indicators.tsv) and save it over the top of the existing file, `config/indicators.tsv`. Then open the file using a spreadsheet to inspect it. Here we have added two new indicators, `201` and `202`, that work with `pr` rather than `tas`. 

7. So now we are ready to go. Firstly, let's see how snakemake responds to this new configuration - lots of new things to do.
```
snakemake -n
```

8. The revised DAG is also more complicated as a result. Open the file `dag_tutorial04.png` and compare it to the previous DAGs.

```
snakemake --dag | dot -Tpng -Grankdir=LR > dag_tutorial04.png
```

9. Make it so!

```
snakemake --cores 1

```

9.  The difference will be most apparent in the output files. Try browsing through them now in a graphics viewer e.g.

```
eog ./outputs/7.plots/
```

10. That concludes this tutorial. KAPy is designed to handle multiple different data sources within the same framework. For example, applying the same processing chains to data from ERA5, CMIP5, and CMIP6 is  possible within the same workflow.

