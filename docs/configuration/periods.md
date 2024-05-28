# KAPy periods configuration

*Calculation periods in KAPy are configured through a tab-separated table, with one row per period. The available options are described here. All options are required*

## Properties

- **`id`** *(['integer', 'string'])*: Unique identifier for the period. This can be numeric, but will be treated as a string.
- **`name`** *(string)*: A longer description of the period. This is typically used in the x-axes of plots, so shouldn't be TOO long!
- **`start`** *(integer)*: The start year of the period. The full year is included in the calculation.
- **`end`** *(integer)*: The end year of the period. The full year is included in the calculation.
