# KAPy indicator configuration

*Configuration of indicators is set through a tab-separated table, with one row per indicator. The available configuration options are described here. All options are required*

## Properties

- **`id`** *(['string', 'integer'])*: Identifier for the indicators. Must be unique.
- **`name`** *(string)*: Name of the indicator.
- **`units`** *(string)*: Units of measurement for the indicator.
- **`variables`**: List of input variables required to calculate the indicator. Must be at least one specified.
  - **One of**
    - *string*
    - *array*
      - **Items** *(string)*
- **`season`**: Season IDs over which the indicator is to be calculated. IDs should match those in the [seasons configuration](seasons.md) table. In addition, `all` selects all seasons.
  - **One of**
    - *string*
    - *array*
      - **Items** *(string)*
- **`statistic`** *(string)*: Metric to be used to calculate the indicator. Must be one of: `["mean"]`.
- **`time_binning`** *(string)*: Time bins over which indicators are calculated. `periods` is defined in the [periods configuration](periods.md) table. Must be one of: `["periods", "years", "months"]`.
