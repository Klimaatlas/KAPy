# Tutorial 01 - Data download with esgpull

## Goal

To familiarise yourself with how to download climate model data of interest from ESGF using the `esgpull` tool.

## Point of departure

This provides a quick standardised way of downloading climate model data which can then be used in the `KAPy` for processing. This is part of the data pre-processing stage done for `KAPy`.

## Instructions
1. The first thing you need before starting the download process using `esgpull` is to make sure that `esgpull` is well installed, and configured in your machine. This process is explained in `Tutorial01`. You also need to have setup authentification credentials for one of the ESGF nodes where the data will be sourced by the `esgpull` tool. For example, you can register and get an ESGF Data Access through the website https://esgf-data.dkrz.de/projects/esgf-dkrz/. Here, in the process of registering, you will set up your `password` and get an `OpenId`. 
   
2. Before `esgpull` can be used for data search and download, check if it is set up and configured correctly. The following command that checks the `esgpull` version installed can be used:
   
```
esgpull -V
```

3. Identify the specifications of the data you want to search and download e.g., `variable` (pr, tas, etc); `project` (CMIP or CORDEX); etc. This can be done using the Facet Search approach. Facests are keywords that can be used with `esgpull` to search for your data of interest. The list of Facets you can use is in the python file `selection.py` found in the `esgpull` root folder you created during installation:
```
/my_esgpull_main_folder/data/selection.py
```

4. You can use the following Facets query to check for the keywords to use in the search for CORDEX data:

```
esgpull search project:CORDEX --facets
```

This gives:\
 `["access",`\
  `"cf_standard_name",`\
  `"data_node",`\
  `"directory_format_template_",`\
 ` "domain",`\
  `"driving_model",`\
  `"ensemble",`\
  `"experiment",`\
  `"experiment_family",`\
  `"index_node",`\
  `"institute",`\
  `"metadata_format",`\
  `"product",`\
  `"project",`\
  `"rcm_name",`\
  `"rcm_version",`\
  `"time_frequency",`\
  `"variable",`\
  `"variable_long_name",`\
  `"version"]'`
  
5. The Facets are not always the same for different projects. For example, the Facets of the CMIP5-based suite of CORDEX models are different from those of the CMIP6 suite of models.
An example of how you can download model data with the following specifications:
    
* temperature;
* downscaled CORDEX models for the Africa domain at 44km resolution;
* at monthly timescale;
* from SMHI Institute who did the downscaling;
* from the MOHC driving model;
* for future projections under the rcp85 scenario;
* for only the first ensemble member of the model.`

You first have to search the data which fits the criteria. The `size` of the datasets requested will also be shown. This gives you a sense of data you are looking for before downloading it. The search is done by the following command:

```
 esgpull search project:CORDEX domain:AFR-44 variable:tas time_frequency:mon ensemble:r1i1p1 institute:SMHI experiment:rcp85 --distrib true
```

This command searches for the `44km` horizontal grid resolution climate model `temperature` data downscaled by the `SMHI` institute for the `Africa` domain under the `CORDEX` project. The data request here is restricted to `monthly` timescale and from only the `first member` of each `model`. The result will show rows of files identified and which can be downloaded. The `size` of a single file per each `id` file will also be shown. This command will show the table below:

 ```
id │                                      dataset                                       │ #  │   size   
════╪════════════════════════════════════════════════════════════════════════════════════╪════╪══════════
  0 │ cordex.output.AFR-44.SMHI.ICHEC-EC-EARTH.rcp85.r1i1p1.RCA4.v1.mon.tas.v20191014    │ 10 │ 78.8 MiB 
  1 │ cordex.output.AFR-44.SMHI.CSIRO-QCCCE-CSIRO-Mk3-6-0.rcp85.r1i1p1.RCA4.v1.mon.tas.… │ 10 │ 79.0 MiB 
  2 │ cordex.output.AFR-44.SMHI.MIROC-MIROC5.rcp85.r1i1p1.RCA4.v1.mon.tas.v20130927      │ 10 │ 79.0 MiB 
  3 │ cordex.output.AFR-44.SMHI.MOHC-HadGEM2-ES.rcp85.r1i1p1.RCA4.v1.mon.tas.v20130927   │ 10 │ 76.5 MiB 
  4 │ cordex.output.AFR-44.SMHI.MPI-M-MPI-ESM-LR.rcp85.r1i1p1.RCA4.v1.mon.tas.v20130927  │ 10 │ 79.8 MiB 
  5 │ cordex.output.AFR-44.SMHI.NCC-NorESM1-M.rcp85.r1i1p1.RCA4.v1.mon.tas.v20130927     │ 10 │ 78.9 MiB 
  6 │ cordex.output.AFR-44.SMHI.CNRM-CERFACS-CNRM-CM5.rcp85.r1i1p1.RCA4.v1.mon.tas.v201… │ 10 │ 79.0 MiB 
  7 │ cordex.output.AFR-44.SMHI.IPSL-IPSL-CM5A-MR.rcp85.r1i1p1.RCA4.v1.mon.tas.v20140612 │ 10 │ 79.0 MiB 
  8 │ cordex.output.AFR-44.SMHI.CCCma-CanESM2.rcp85.r1i1p1.RCA4.v1.mon.tas.v20130927     │ 10 │ 78.4 MiB 
  9 │ cordex.output.AFR-44.SMHI.NOAA-GFDL-GFDL-ESM2M.rcp85.r1i1p1.RCA4.v1.mon.tas.v2013… │ 10 │ 78.9 MiB 
  ```


* PS. You can also search for `multiple` comma separated `variables` at once. For example, you can search for `precipitation` and `temperature` together by specifying `variable:tas,pr` and can also specify different timescales e.g `time_frequency:mon,day`.

7. You can see detailed information about one of the models before downloading the whole dataset. This is achieved by adding `--detail 0` in front of the previous command for data `esgpull search`. This will display detailed information about the first result (`index 0`) in the search results i.e. the first dataset in the list. That is:

```
 esgpull search project:CORDEX domain:AFR-44 variable:tas time_frequency:mon ensemble:r1i1p1 institute:SMHI experiment:rcp85 --distrib true --detail 0
```
This command will display the information of the first index, in this case, the information about the first model in the list i.e `ICHEC-EC-EARTH`:
```
DATASET
└── data_node:          esg-dn1.nsc.liu.se                                                               
    domain:             AFR-44                                                                           
    driving_model:      ICHEC-EC-EARTH                                                                   
    ensemble:           r1i1p1                                                                           
    experiment:         rcp85                                                                            
    experiment_family:  All, RCP                                                                         
    index_node:         esg-dn1.nsc.liu.se                                                               
    instance_id:        cordex.output.AFR-44.SMHI.ICHEC-EC-EARTH.rcp85.r1i1p1.RCA4.v1.mon.tas.v20191014  
    institute:          SMHI                                                                             
    master_id:          cordex.output.AFR-44.SMHI.ICHEC-EC-EARTH.rcp85.r1i1p1.RCA4.v1.mon.tas            
    project:            CORDEX                                                                           
    rcm_name:           RCA4                                                                             
    time_frequency:     mon                                                                              
    title:              cordex.output.AFR-44.SMHI.ICHEC-EC-EARTH.rcp85.r1i1p1.RCA4.v1.mon.tas            
    url:                http://esg-dn1.nsc.liu.se/thredds/catalog/esgcet/167/cordex.output.AFR-44.SMHI.I…
    variable:           tas                                                                              
    variable_long_name: Near-Surface Air Temperature
```


8. After being satisfied that `esgpull` has managed to search and find the data you queried, use the `èsgpull add` function to submit your request/query to a queue for it to be considered for download. To do this, replace the "`search`” word with “`add`” to the previous command to give:

```
esgpull add project:CORDEX domain:AFR-44 variable:tas time_frequency:mon ensemble:r1i1p1 institute:SMHI experiment:rcp85 --distrib true
```

9. If the submission is accepted, you will get a `query number` and a thumbs up.
```
<801f70> untracked
└── distrib:        True  
    domain:         AFR-44
    ensemble:       r1i1p1
    experiment:     rcp85 
    institute:      SMHI  
    project:        CORDEX
    time_frequency: mon   
    variable:       tas   
New query added: <801f70>
👍 1 new query added.
```
11. Tracking your `query`\

   The query is `untracked` by default to avoid mistakenly requesting to download a huge unwanted dataset by mistake. If you are sure, you can automate the command so that it switches the tracking function on. You do this by adding the word `track` at the end of the `esgpull add` command.
Or you can run `esgpull track <query number>` after running the `add` command. In the command below, replace `<query number>` with the actual query number generated in the previous step

```
esgpull track <query number>
```
Confirm that you want to apply the changes by typing `y`, and you will get a thumbs up.

PS. This stage is necessary as you cannot run the next stage if your query is `untracked`.

11. Updating the query\
It is always advisable to update the query (the query number generated after running the previous `track` command) to ensure the latest and all the datasets available to date are pulled:
```
esgpull update <query number>
```

   This will let you know the `total number` of files available for download. It will prompt you to confirm if you want to add the files to the list. Importantly, it will tell you the `total size` of the whole dataset. In this case, its `787.4mb`

12. The last stage is about downloading the pulled/identified data. The following command is used bearing in mind to use the query number generated after running the `esgpull update` command:

```
esgpull downlaod <query number>
```

   This will commence the data download into the `data` folder found in your folder you specified when installing and setting up `esgpull`. The time it will take will depend on the data requested and your internet speed. The progress of the download will be shown when the data download starts.

13. Cecking the status of the esgpull queries.\
    You can check the status of the queries, whether there were errors, dowload paused, download cancled etc.
```
esgpull status
```
If any of these optioins are true, you can use the retry command to resume the downloads. See next step.
    
15. In case some files fail to download for some reason or there are errors when downloading, you can use the `retry` function to retry the download. To check which option to use which best fits your circumstances, use:
```
esgpull retry -h
```
The options available with the retry command depening on circumstance are\
`[[new|queued|starting|started|pausing|paused|error|cancelled|done]]`


Done!!!
