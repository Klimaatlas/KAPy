# Tutorial 1 - A basic run through

## Goal

To familiarise yourself with KAPy via a minimum working example of setting up and running an analysis.

## Point of departure

A configured fresh version of KAPy. See the "Getting Started" section of README.md for more on this.

## Instructions

1. KAPy comes with the necessary configuration files already in place. Configuration files are stored in `./config`. Open this directory, either on the webpage or in your terminal, and note the files that are present. The primary configuration file `./config/config.yaml` provides general coordination, while the tabular configuration files (ending with `.tsv`) are spreadsheet-like tables that provide configuration of indvidiual aspects (e.g. inputs, indicators, scenarios etc).
  
2. Open `./config/config.yaml` in a text viewer (e.g. `vi`, `less`) and browse through it. Note in particular the definition of the spatial domains, directories, and other miscellaneous options, together with links to the other configuration tables defining inputs, indicators etc.

3. Now open one of these configuration tables e.g `./config/inputs.tsv`. You will see a range of options configured as columns, while each row corresponds to an individual input data source. Details of all options can be found in the [configuration documentation](./docs/Configuration.md). Open some of the other configuration tables as well to see the differences.

4. Ok, before we get going, make sure that you have the KAPy environment activated - you should see `(KAPy)` in your command prompt. If you have `(base)` or similar activate it with the following command. If you're unsure, it doesn't hurt to activate it again.

```
conda activate KAPy
```

5. Now, before running anything, we need some data to work on. Download the [example working dataset](https://download.dmi.dk/Research_Projects/KAPy/tas_example_dataset.zip) into a temporary directory. This dataset provides a small set of CORDEX Africa monthly temperature outputs over Ghana for two different climate emissions scenarios, together with corresponding data from ERA5.

6. Unzip the .zip file. You should get two directories: `CORDEX` and `ERA5_monthly`.

7. Move the two directories (and their contents) into the KAPy folder `./resources/`. The `resources` folder is generally used for input files and files that don't change, while outputs are written to `./results`. These directories can be configured in `./config/config.yaml`. 

8. We are now actually ready to roll. KAPy is run via the `snakemake` command - you can get lots of help directly from snakemake using

```
snakemake -h
```

9. Before actually making any changes to the disk, it can be a good idea to check when snakemake is actually going to do. The `-n` switch forces a dry-run. Try it:

```
snakemake -n
```
10. You will get an overview of all of the different targets that are going to be run. Now, lets run them all. The `--cores` argument is required by snakemake - in the example below we only use one processor, handling one job at a time, but feel free to scale this up depending on the resources available. One of the beauties of snakemake is that it scales well from laptops to clusters - you can easily switch between the two by simply adjusting the number of resources used.
```
snakemake --cores 1
```

11. Snakemake will take a few minutes to run - take note of the outputs, which detail what is being done at each step, together with the input and output files.

12. Now have a look in `./results` and the subdirectories there. You will see that they have all be filled out with the corresponding files.

13. A Jupyter notebook is used to give a quick overview of the results. Note that this is intended to be generic and work for all possible configurations - the plot that you actually want is most likely not there. Nevertheless, it does still provide a nice overview. Open the file `./results/7.notebooks/Output_overview.py.html` in e.g. a browser to view the results:

```
firefox results/7.notebooks/Output_overview.py.html 
```

16. Ka pai! You've finished your first analysis in KAPy! You can learn more in the other [Tutorials](README.md) that follow on from this point.
