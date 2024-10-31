# Tutorial 5 - Using a shapefile-specified domain for area averaging

## Goal

To learn how a new shapefile is sourced and configured in KAPy.

## Point of departure

This tutorial follows on directly from the end of [Tutorial 1](Tutorial01.md).

## Instructions

1. In Tutorial 1, you performed a complete run of a KAPy pipeline, starting from a fresh installation.
That configuration defines a domain based on a cutout box (covering Ghana's boundaries) done on the original input climate data. The extent of this box is determined by the minimum and maximum latitude and longitude bounds of Ghana as specified in the `config.yaml` file. The area averaging is done based on this domain. In a real setting, area averaging would ideally be done on a polygon specified through a `shapefile`. This will allow production of results for specific areas e.g national, provincial etc.

2. First, we need to create a folder where a shapefile is located/placed. A shapefile is not a single file but a collection of several files with different extensions, working together to represent spatial data.
   While in KAPy root folder, create the `shapefiles` folder into the `resources` folder.

```
mkdir ./resources/shapefiles/*
```

3. Get a shapefile of interest (Ghana in this case). For this Ghana example, you can use the one [here](Tutorial05_files) 
 Copy it into the `resources/shapefiles/` folder where the data folders were copied to in the previous Tutorials. Now in `resources/`, you should see three sub- folders `CORDEX`, `ERA5_monthly` and `shapefiles`. Check the contents of the shapefile directory - you should now see files starting with both `Ghana_`.

```
ls ./resources/shapefiles/*
```

3. The shapefile specifications is defined via the config file `./config/config.yaml`. Open this file in a text editor (e.g. `vi`). The path of the shapefile is specified under the `configuration options`. To direct KAPy to use this shapefile in the area averaging over polygons of interest specified in the shapefile, define the path where the shapefile folder is by editing the `shapefile` line under `arealstats` subsection. The commented lines under this section show an example how this change can look like. You will end up with something like this:

```
# Configuration options------------------------------------
arealstats:
    useAreaWeighting: True
    shapefile: 'resources/shapefiles/Ghana_regions.shp'
    idColumn: 'ADM1_PCODE'
    #shapefile: 'resources/shapefiles/Ghana_regions.shp'
    #idColumn: 'ADM1_PCODE'
```

5. So now we are ready to go. Firstly, let's see how snakemake responds to this new configuration - lots of  things to do. 

```
snakemake -n
```
KAPy will show that it needs to do a lot of things to effect these changes. This is because it has flagged that now it is asked to use shapefile polygons for area averaging and consequently redo the line- and box- plots.

6. The revised DAG is also even more complicated as a result. Open the file `dag_tutorial05.png` and compare it to the previous DAGs.

```
snakemake --dag | dot -Tpng -Grankdir=LR > dag_tutorial04.png
```

7. Then, make it so!

```
snakemake --cores 1

```

9.  The difference will be most apparent in the output files created. Try browsing through them 
```
ls ./results/6.arealstats/
```
and also try browsing through the the plots in a graphics viewer e.g
```
eog ./results/6.plots/
```

10. That concludes this tutorial. 
