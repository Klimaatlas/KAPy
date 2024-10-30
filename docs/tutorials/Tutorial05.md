# Tutorial 5 - Using a shapefile-specified domain

## Goal

To learn how a new shapefile is sourced and configured in KAPy.

## Point of departure

This tutorial follows on directly from the end of [Tutorial 1](Tutorial01.md).

## Instructions

1. In Tutorial 1, you performed a complete run of a KAPy pipeline, starting from a fresh installation.
That configuration defines a domain based on a cutout box (covering Ghana's boundaries) done on the original input climate data. The extent of this box is determined by the minimum and maximum latitude and longitude bounds of Ghana as specified in the `config.yaml` file. In a real setting especially for area averaging, we would ideally use a domain defined by a polygon specified through a `shapefile`.

2. First, we need to get a shapefile of interest (Ghana shapefeile in this case). Download a shapefiles folder with the shapefile of interest. For the example of Ghana, you can use the one [here](Tutorial05_files) 
 Copy it into the `resources/` folder where the data folders were copied to. Now in `resources/`, you should see three sub-folders `CORDEX`, `ERA5_monthly` and `shapefiles`. Check the contents of the shapefile directory - you should see files starting with both `GHA_*` now.

```
ls resources/shapefile/*
```

3. The shapefile specifications is defined via the config file `./config/config.yaml`. Open this file in a text editor (e.g. `vi`). The path of the shapefile is specified under the `configuration options`. To direct KAPy to use this shapefile in the cuttingout of the domain, do this by changing `None` to `shapefile` in the method part of the `cutouts section` of  the `config.yaml` file to end up with something like this:

```
cutouts:
    method: 'shapefile'
    # method: 'lonlatbox'
```
4. Since the intention is to have KAPy use data from a domain cutout using a shapefile, we need the `results` folder to be empty or not exist so that it can be created by KAPy and receive new results with these changes. To allow KAPy to rerun to effect the changes and save, rename the current `results` folder to `old_results` to make way for KAPy to create the new results folder. While in the KAPy root folder:

```
mv results/ old_results
```

5. So now we are ready to go. Firstly, let's see how snakemake responds to this new configuration - lots of  things to do. KAPy will show that it needs to redo everything. This is because it has flagged that there are no results present as the `results` folder is missing.
```
snakemake -n

```

6. Then, make it so!

```
snakemake --cores 1

```

9.  The difference will be most apparent in the plot files created. Compare the plots in the new results folder to the ones in the `old_results` folder you renamed in `step 4`. Try browsing through them in a graphics viewer e.g.

```
eog ./results/6.plots/
```
and 
```
eog ./old_results/6.plots/
```

10. That concludes this tutorial. If you wnat to use a different a different shapefile, place the new shapefile in `resources/shapefile/`, and then follow again the steps in this tutorial. You can rename the previosu results folder using a more intuitive name e.g., based on the domain of the shapefile used.

