# KAPy configuration options

*Configuration schema for KAPy configuration objects. These configurations are usually stored in the `config.yaml` file in the root directory of the project.*

## Properties

- **`configurationTables`**: Paths to configuration tables. See the documentation for each table separately. Cannot contain additional properties.
  - **`inputs`** *(string, required)*: Path to input configuration table, relative to working directory. See [inputs.md](inputs.md) for more detail.
  - **`secondaryVars`** *(string)*: Path to configuration table for secondary variables, relative to working directory. See [derivedVars.md](derivedVars.md) for more details. Optional - if omitted, no secondary variables will be generated.
  - **`indicators`** *(string, required)*: Path to indicator configuration table, relative to working directory. See [indicators.md](indicators.md) for more detail.
  - **`scenarios`** *(string, required)*: Path to scenario configuration table, relative to working directory. See [scenarios.md](scenarios.md) for more detail.
  - **`periods`** *(string, required)*: Path to period configuration table, relative to working directory. See [periods.md](periods.md) for more detail.
  - **`seasons`** *(string, required)*: Path to season configuration table, relative to working directory. See [seasons.md](seasons.md) for more detail.
- **`outputGrid`**: Defines the common output grid onto which KAPy interpolates all indicators before calculating ensemble statistics. Multiple approaches to regridding can be configured, as described below.
  - **One of**
    - *object*: Omit the regridding step. Assumes that all files within an input type are on the same grid, which will be used as the output grid. Cannot contain additional properties.
      - **`regriddingEngine`** *(string, required)*: Must be one of: `["None"]`.
- **`arealstats`** *(object)*: Cannot contain additional properties.
  - **`calcForMembers`** *(boolean, required)*: Should the areal statistics be calculated for the individual ensemble members as well as for the entire ensemble. `true` or `false`.
- **`dirs`** *(object)*: Directories for storing output and intermediate files. Can be specified as either absolute paths, or relative to the working directory. See the [KAPy concepts](../KAPy_concepts.md) documentation for a more detailed description of these items. Cannot contain additional properties.
  - **`variables`** *(string, required)*: Directory for storing variables.
  - **`indicators`** *(string, required)*: Directory for storing indicators variables.
  - **`regridded`** *(string, required)*: Directory for storing indicators regridded to a common grid.
  - **`ensstats`** *(string, required)*: Directory for storing enssemble statistics.
  - **`arealstats`** *(string, required)*: Directory for storing statistics calculated over areas.
  - **`notebooks`** *(string, required)*: Directory for storing compiled Jupyter notebooks.
  - **`plots`** *(string, required)*: Directory for storing output plots.
- **`ensembles`** *(object)*: Specify the percentiles [0-100] calculated from the ensemble. We allow three values, corresponding to the upper and lower confidence limits, and the central value. Cannot contain additional properties.
  - **`upperPercentile`** *(integer, required)*: Exclusive minimum: `0`. Exclusive maximum: `100`.
  - **`centralPercentile`** *(integer, required)*: Exclusive minimum: `0`. Exclusive maximum: `100`.
  - **`lowerPercentile`** *(integer, required)*: Exclusive minimum: `0`. Exclusive maximum: `100`.
