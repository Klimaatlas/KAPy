# Tutorial 01 - Installation guide: esgpull

## Goal

To familiarise yourself with how to install the `esgpull` tool which is used to search and download climate model data from the ESGF platform.

## Point of departure

This is a precursor step before using the `esgpull` tool for quick and standardized climate model data download. This is part of the  preprocessing stage which can be done to get data used in `KAPy`.

## Instructions
First, you need to install the `esgpull` using the instructions here.
     https://esgf.github.io/esgf-download/installation/
   
## Setting up the `esgpull`
1. Once the `esgpull` tool is installed, there is a need to set it up before use for data search and download so that you can use its full functionality. A self-install command is used as a first step in the setting up of the tool. Although this sounds like one is installing the tool for the second time, but what this stage does is to give the `esgpull` tool write permissions where the data will be downloaded. This is done by specifying/creating the `esgpull` root folder where the `data` folder for the downloads will be found. The self-install command is:

```
esgpull self install
```
This will prompt you to define/enter a folder of your choice which is going to be the esgpull root folder. For example, where ESGpull is defined as the root folder:

```
Install location (/home/WDIR/.esgpull): ESGpull
```

3. You have an option to also include your name. You are going to be prompted to enter this just after you define the root folder in the previous step.
```
Enter optional name:
Name (optional): John Doe
```

4. Then you will get something like:\
`Creating install directory and files at` "The-folder-you-specified-in-the-directory-are-currently-in" \
`Install config added to /home/WDIR/.config/esgpull/installs.json`

5. Lastly, check if everything is setup well and `esgpull` is ready for use using the following command :

```
esgpull --version
```
