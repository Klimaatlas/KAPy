# KAPy seasons configuration

*Seasonal calculations in KAPy are configured through a tab-separated table, with one row per season. The available options are described here. All options are required*

## Properties

- <a id="properties/id"></a>**`id`** *(string, required)*: Unique identifier for the season. It is recommended to use a short descriptive string e.g `JJA`. Note that the id `all` cannot be used, as this is reserved for use in selecting all seasons in the indicator table. Must not contain spaces. Must match pattern: `^[^ ]+$` ([Test](https://regexr.com/?expression=%5E%5B%5E%20%5D%2B%24)). Items must be unique.
- <a id="properties/enabled"></a>**`enabled`** *(string or null, required)*: Determines whether the row be used in the workflow. A non-empty value indicates not to use that row.
- <a id="properties/name"></a>**`name`** *(string, required)*: A longer description of the season. This is typically used in output files.
- <a id="properties/months"></a>**`months`** *(string, required)*: The month(s) to include in the seasonal definition, defined by their numbers. Multiple months are specified as a common-separated list. Duplicates are not allowed.
