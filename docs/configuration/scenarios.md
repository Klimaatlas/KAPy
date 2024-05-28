# KAPy emission scenarios configuration

*Emissions scenarios in KAPy are declared through a tab-separated table, with one row per scenario. The available options are described here. All options are required*

## Properties

- **`id`** *(string)*: Unique identifier for the scenario. This can be numeric, but as it will be used in e.g. filenames, it is recommended to use a short descriptive string e.g `rcp26`.
- **`description`** *(string)*: A longer description of the scenario. This is typically used in the legends of plots, so shouldn't be TOO long!
- **`regex`** *(string)*: A regular expression used to group input files together according to their scenarios. Files that match the regex will be associated with the individual scenario. Failure to match any regexs will throw an error if the input is marked as having scenarios (see the `hasScenarios` option in the [input configuation table](inputs.md)). e.g. '`.*_(historical|rcp26)_.*`' .
- **`colour`** *(string)*: Colour to be used for this scenario when generating plots.
