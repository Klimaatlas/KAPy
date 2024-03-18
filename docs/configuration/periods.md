# KAPy periods configuration

*Calculation periods in KAPy are configured through a tab-separated table, with one row per period. The available options are described here. All options are required*

## Properties

- **`id`** *(['integer', 'string'])*: Unique identifier for the period. This can be numeric, but as it will be used in e.g. output files, it is recommended to use a short descriptive string e.g `hist`.
- **`name`** *(string)*: A longer description of the period. This is typically used in the x-axes of plots, so shouldn't be TOO long! Remember that you can include linebreaks using the `\n` character. e.g. `Historical\n(1981-2010)` .
- **`start`** *(integer)*: The start year of the period. The full year is included in the calculation.
- **`end`** *(integer)*: The end year of the period. The full year is included in the calculation.
