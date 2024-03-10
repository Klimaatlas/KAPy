# Tutorial 01 - Installation guide: esgpull

## Goal

To familiarise yourself with how to download climate model data of interest ESGF using the `esgpull` tool.

## Point of departure

This provides a quick standardised way of downloading climate model data which can then be used in the `KAPy` for processing. This is part of the data preprocessing stage done in `KAPy`.

## Instructions
1. The first thing you need before starting the download process using `esgpull` is to make sure that `esgpull` is well installed, and configured. You also need to have setup authentification credentials for one of the ESGF nodes where the data will be sourced by `esgpull`. This process is explained in `Tutorial ***`.


Next, we need to setup the Python environment, containing the packages used by KAPy. Add-on libraries in Python are referred to as "packages" and their installation is maintained by a package manager, of which there are many to choose from (e.g. Anaconda, Conda, Miniconda, Mamba, Micromamba etc). The example code given here is for the Conda package manager - you can download it from https://conda.io/projects/conda/en/latest/index.html if you don't have it already, but KAPy should work just as well with other package managers. The examples are also for a Linux environment - however, a similar approach will hold if you want to try and get KAPy running in Windows.
