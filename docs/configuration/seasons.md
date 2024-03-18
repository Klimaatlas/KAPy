# KAPy seasons configuration

*Seasonal calculations in KAPy are configured through a tab-separated table, with one row per season. The available options are described here. All options are required*

## Properties

- **`id`** *(string)*: Unique identifier for the season. As it will be used in part for the naming of output files, it is recommended to use a short descriptive string e.g `JJA`.
- **`name`** *(string)*: A longer description of the season. This is typically used in output files.
- **`months`** *(array)*: The month(s) to include in the seasonal definition, defined by their numbers. Multiple months are specified as a common-separated list. Duplicates are not allowed.
  - **Items** *(integer)*: Minimum: `1`. Maximum: `12`.
