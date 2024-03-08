# Measurement Schema

*Schema for representing measurements.*

## Properties

- **`id`** *(['string', 'integer'])*: Identifier for the indicators. Must be unique.
- **`name`** *(string)*: Name of the indicator.
- **`units`** *(string)*: Units of measurement for the indicator.
- **`variables`**: List of input variables required to calculate the indicator. Must be at least one specified.
  - **One of**
    - *['string', 'null']*
    - *array*
      - **Items** *(string)*
- **`season`**: Season IDs over which the indicator is to be calculated.  in the seasons .
  - **One of**
    - *string*
    - *array*
      - **Items** *(string)*
