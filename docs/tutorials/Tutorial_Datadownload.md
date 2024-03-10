# Tutorial 00 - Data download with esgpull

## Goal

To familiarise yourself with how to download climate model data of interest ESGF using the `esgpull` tool.

## Point of departure

This provides a quick standardised way of downloading climate model data which can then be used in the `KAPy` for processing. This is part of the data preprocessing stage done in `KAPy`.

## Instructions
1. The first thing you need before starting the download process using `esgpull` is to make sure that `esgpull` is well installed, and configured. You also need to have setup authentification credentials for one of the ESGF nodes where the data will be sourced by `esgpull`. This process is explained in `Tutorial ***`.
   
2. Before `esgpull` can be used for data search and download, check if it is set up and configured correctly. The following command can be used which checks the `esgpull` version installed.
   
```
esgpull -V
```

3. Identify the specs of the data you want to search and download e.g., variable (pr, tas, etc), project (CMIP or CORDEX), etc. This can be done using the Facet Search Approach. Facests are keywords that can be used with `esgpull` to search for your data of interest. The list of Facets one can use can be found in the `selection.py` file found in the esgpull root folder you would have created during installation:
```
/my_esgpull_main_folder/data/selection.py
```

4. The Facets are not always the same for different projects. The Facets of the CMIP5-based suite of CORDEX models are different from the CMIP6 suite of models. An example of how you can download model data with the following specifications:
    
* temperature and precipitation;
* downscaled CORDEX model for the Africa domain at 0.5degrees;
* at monthly timescale;
* from SMHI Institute who did the downscaling;
* from the MOHC driving model;
* for future projections under the rcp85 scenario;
* for only the first ensemble member of the model.`

You can use the following Facets query to check the keywords you can use in the search for CORDEX data:

```
esgpull search project:CORDEX --facets
```

This gives:
* `["access",
  "cf_standard_name",
  "data_node",
  "directory_format_template_",
  "domain",
  "driving_model",
  "ensemble",
  "experiment",
  "experiment_family",
  "index_node",
  "institute",
  "metadata_format",
  "product",
  "project",
  "rcm_name",
  "rcm_version",
  "time_frequency",
  "variable",
  "variable_long_name",
  "version"]'`

5. Search for the data which fits the criteria of the above example. The size of the datasets requested will also be shown. This gives you the sense of data you are looking for before downloading it.

```
 esgpull search project:CORDEX domain:AFR-44 variable:tas time_frequency:mon ensemble:r1i1p1 institute:SMHI experiment:rcp85 --distrib true
```

This command searches for the 44km horizontal grid resolution climate model temperature data downscaled by SMHI institute for the Africa domain under the CORDEX project. The data is restricted to monthly timescale and from only the first member of each model:

<img width="836" alt="image" src="https://github.com/ShingiNangombe/KAPy/assets/63850110/041059ac-1821-496c-97e8-627ba04a9741">

   This shows rows representing each downscaled GCM. There are 10 files identified for each model and the size of each file is also shown.

* PS. You can also search for multiple variables at once. For example, you can search for precipitation and temperature by using `variable:tas,pr` and/or can also use different timescales e.g `time_frequency:mon,day`.

6. You can see detailed information of one of the models before downloading the whole dataset. This is achieved by adding ` --detail 0 ` in front of the previous command for data `esgpull search'. This will display detailed information about the first result (index 0) in the search results i.e. the first dataset in the list. That is:

```
 esgpull search project:CORDEX domain:AFR-44 variable:tas time_frequency:mon ensemble:r1i1p1 institute:SMHI experiment:rcp85 --distrib true --detail 0
```

7. After being satisfied that `esgpull` has managed to search and find the data you queried, use the `èsgpull add` function to submit your request/query to a queue for it to be considered for download. To do this, replace the “search” word with “add” to the command. Thus,  the command will be:

```
esgpull add project:CORDEX domain:AFR-44 variable:tas time_frequency:mon ensemble:r1i1p1 institute:SMHI experiment:rcp85 --distrib true
```

8. If the submission is accepted, you will get a query number and a thumbs up. It gives the following: 

* <img width="269" alt="Screenshot 2024-03-09 at 08 58 35" src="https://github.com/ShingiNangombe/KAPy/assets/63850110/1b9f0cd7-a2fa-49ad-92f6-3cdfd6cab404">

9. Tracking the query

   The query is `untracked` by default to avoid mistakenly requesting to download a huge unwanted dataset by mistake. If you are sure, You can automate the command so that it switches the tracking function on. You do this by adding the word `track` on the `esgpull add` command.
Or you can run `esgpull track <querry #>` after running the add command.

```
esgpull track <querry number>
```

   PS. This stage is necessary as you cannot run the next stage if your queries are `untracked`.

10. Updating the query
It is always advisable to update the query (the query number generated after running the previous “`track` command) to ensure the latest and all the datasets available to date are pulled
```
esgpull update <query number>
```

   This will let you know the total number of files available for download after the updating is done. It will prompt you to confirm if you want to add the new files to update the list. Importantly, it will tell the total size of the whole dataset. In this case, its `787.4mb`

11. The last stage is about downloading the pulled/identified data. The following command is used bearing in mind to use the query number generated after running the `èsgpull update` command:

```
esgpull downlaod <query number>
```

   This will commence the data download into the folder you specified when installing and setting up `esgpull`. The time it will take will depend on the data requested and your internet speed.

   In case some files fail for some reason or there are errors when downloading, you can use the `retry` function to retry the download. To check which option to use which best fits your circumstances, use:
```
esgpull retry -h
```


