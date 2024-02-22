# Tutorial 1 - A basic run through

## Goal

To familiarise yourself with a minimum working example of setting up and running an analysis with KAPy.

## Point of departure

A configured fresh version of KAPy. See the "Getting Started" section of README.md for more on this.

## Instructions

1. Start by choosing the KAPy configuration to work with. The "test" configuration in `./configs/test` is the one to use here. Copy (or soft-link) the `config.yaml` file found there into the KAPy root directory e.g

```
cp ./configs/tutorial/config.yaml .
```

2. Open `config.yaml` in a text viewer (e.g. vi, less) and browse through it. Note in particular the definition of the spatial domains, the input files, and the indicators. 

3. Now open the file `./configs/defaults.yaml` and compare with `config.yaml`. `defaults.yaml` defines lot more options used by KAPy, but these are less frequently modified than those in `config.yaml`. In particular, pay attention to the "dirs" options, which defines the names of the default files. If you wish to modify one of the defaults, it is best to do it in `config.yaml`- values defined here will override the defaults. Details of all configuration options can be found in [./docs/Configuration.md]. 

4. Before running anything, we make sure that we have some working directories. The script `./Setup.py` takes care of setting these up automagically, based on the values defined in the config file. Run it.

```
./Setup.py
```

5. Do a quick check of the `./workDir/` directory - you should now see a load of directories waiting to receive data.


6. So now we need some data. Download the example working dataset into a temporary directory from here https://download.dmi.dk/Research_Projects/KAPy/tas_example_dataset.zip This dataset provides a small set of CORDEX Africa monthly temperature outputs over Ghana for two different climate emissions scenarios, together with corresponding data from ERA5.

7. Unzip the .zip file. You should get two directories: "CORDEX" and "ERA5_monthly".

8. Move the two directories (and their contents) into the KAPy folder `./workDir/1.inputs/`. 

9. We are now actually ready to roll. KAPy is run via the `snakemake` command - you can get lots of help directly from snakemake using

```
snakemake -h
```

10. Before actually making any changes to the disk, it can be a good idea to check when snakemake is actually going to do. The `-n` switch forces a dry-run. Try it:

```
snakemake -n
```
11. You will get an overview of all of the different targets that are going to be run. Now, lets run them all. The `--cores` argument is required by snakemake - in the example below we only use one processor, handling one job at a time, but feel free to scale this up depending on the resources available. One of the beauties of snakemake is that it scales well from laptops to clusters - you can easily switch between the two by simply adjusting the number of resources used.
```
snakemake --cores 1
```

12. Snakemake will take a few minutes to run - take note of the outputs, which detail what is being done at each step, together with the input and output files.  
