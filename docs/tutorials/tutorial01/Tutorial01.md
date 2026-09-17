# Tutorial 1 – Your first KAPy workflow

## Goal

To familiarise yourself with KAPy by setting up, inspecting and running a minimum working example.

## What are we going to do?

This tutorial works with a small set of monthly temperature projections over Ghana, extracted from the CORDEX Africa ensemble under two future emissions scenarios.

KAPy will generate a single indicator — the annual mean temperature calculated for 30-year periods — for both datasets, without bias adjustment. Most of the tutorial is devoted to exploring the configuration of a working KAPy project and understanding what happens when the workflow is run.

## Before you start

You should have a freshly created KAPy project, generated using Cookiecutter. See the [Getting Started](../../../README.md) section of the README for more information, or the [installation guide](../../installation.md).

The KAPy cookiecutter template allows for both a **simple** and a **full** configuration. This tutorial uses the simple configuration, which is the default when creating a new KAPy project.

## Instructions

1. **Explore the project**

   Open your KAPy project directory, for example:

   ```bash
   cd <my_kapy_project>
   ```

   A KAPy project contains configuration, input data and output data, together with the files needed to run the workflow.

2. **Explore the configuration**

   Configuration files are stored in `./config`. Open this directory and look at the files that are present.

   The main configuration file, `./config/config.yaml`, acts as the entry point to the other configuration tables. The tabular configuration files (ending in `.tsv`) are tab-separated tables that contain the configuration for individual aspects of the workflow, such as inputs and indicators.

3. **Explore `config.yaml`**

   Open `./config/config.yaml` in a text viewer such as `vi` or `less`, and browse through it.

   Note in particular the definitions of the parameters such as cutouts and grids,, as well as the links to the other configuration tables defining inputs, indicators, and so on.

   More information about these options can be found in the [configuration file documentation](../../configuration/config.md).

4. **Explore the configuration tables**

   Open one of the configuration tables, for example `./config/inputs.tsv`, using a spreadsheet application such as LibreOffice or Excel.

   You will see a range of configuration options arranged as columns, with each row corresponding to an individual input data source. Because these are tab-separated files, it is not recommended to edit them using a text editor such as `vi`: it is easy to lose track of which tabs separate the columns.

   Details of the input configuration options can be found in the [input configuration documentation](../../configuration/inputs.md).

   Have a look at the other configuration tables as well to see how they differ. A full overview of the available configuration options is provided in the [configuration overview](../../Configuration.md).

5. **Explore the input data**

   It is also worth exploring the `./inputs` directory. This is where input data is stored. The Cookiecutter template takes care of downloading the trial dataset and placing it in this directory.

   KAPy includes `ncview`, a simple graphical viewer for NetCDF files. Try opening one of the input files:

   ```bash
   ncview tas_Ghana-44_NCC-NorESM1-M_rcp85_r1i1p1_SMHI-RCA4_v1_mon_209601_210012.nc
   ```

   This will open the file in `ncview`. Click on `tas` to see the temperature data, and use the forward arrow to animate it.

6. **Activate the KAPy environment**

   Before running KAPy, make sure that the KAPy Conda environment is activated. You should see `(KAPy)` at the beginning of your command prompt.

   If you see `(base)` or something similar instead, activate the KAPy environment with:

   ```bash
   conda activate KAPy
   ```

   If you're unsure whether the environment is already active, it doesn't hurt to run the command again.

7. **Check what KAPy is going to do**

   KAPy is run through the `snakemake` command. Before actually making any changes to the disk, it is useful to check what Snakemake plans to do. The `-n` option performs a **dry run**: Snakemake builds the workflow and reports the jobs that would be executed, but does not actually run them.

   Try it:

   ```bash
   snakemake -n
   ```

   You will get an overview of the jobs that KAPy would run and the files they would create.

   > **Tip:** A dry run is particularly useful for larger analyses. It allows you to check that your configuration is doing what you expect before starting a potentially long or resource-intensive calculation.

8. **Run the workflow**

   Now let's actually run the workflow.

   Snakemake needs to be told how many CPU cores it is allowed to use. In this example we use one core, which is sufficient for this small analysis:

   ```bash
   snakemake --cores 1
   ```

   For larger analyses, you can increase the number of cores according to the resources available. Snakemake can also be configured to run workflows on larger computing systems.

9. **Watch the workflow run**

   As the workflow runs, Snakemake will report each job as it is executed. Take a moment to look at the messages: they show which KAPy processing step is running and which files are being used and created.

   Snakemake should take a few minutes to complete for this example.

10. **Explore the outputs**

    Now explore the `./outputs` directory and its subdirectories.

    You should see files corresponding to the different stages of the workflow. The dry run did not create these files — they have now been produced by actually running the KAPy workflow.

11. **Ka pai!**

    You've completed your first analysis in KAPy! 🎉

## Next steps

You now have a working KAPy project and have run a complete analysis. Where you go next depends on what you would like to explore:

* **Explore the results:** Learn how to inspect and visualise the results in the [visualisation tutorial](../visualisation/Visualisation.md).

* **Understand the workflow:** Move on to [Tutorial 2](../tutorial02/Tutorial02.md) to learn how KAPy controls and organises the workflow.

* **Explore the documentation:** Return to the [documentation overview](../../README.md) for more information about KAPy and its configuration.
