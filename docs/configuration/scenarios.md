# KAPy emission scenarios configuration

*Emissions scenarios in KAPy are declared through a tab-separated table, with one row per scenario. The available options are described here. All options are required*

## Properties

- **`id`** *(string)*: Unique identifier for the scenario. This can be numeric, but as it will be used in e.g. filenames, it is recommended to use a short descriptive string e.g `rcp26`.
- **`description`** *(string)*: A longer description of the scenario. This is typically used in the legends of plots, so shouldn't be TOO long!
- **`scenarioStrings`** *(array)*: A comma-separated list of strings used to group input files together to form the primary variable inputs. e.g. '`_historical_,_rcp26_`'. The string is removed from the stem once it's found, so be sure to include all delimiters i.e. '_' symbols. All elements in the list need to be found before the grouping of files takes place. .
- **`colour`** *(string)*: Colour to be used for this scenario when generating plots.
