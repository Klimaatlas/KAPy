# KAPy configuration options

*Configuration schema for KAPy configuration objects. These configurations are usually stored in the `config.yaml` file in the root directory of the project.*

## Properties

- **`domain`** *(object)*: Defines the spatial region-of-interest that KAPy should perform the analysis over. Cannot contain additional properties.
  - **`xmin`** *(number, required)*: Western boundary of domain. .
  - **`xmax`** *(number, required)*: Eastern boundary of domain. .
  - **`ymin`** *(number, required)*: Southern boundary of domain. .
  - **`ymax`** *(number, required)*: Northern boundary of domain. .
- **`configurationTables`**: Paths to configuration tables. See the documentation for each table separately. Cannot contain additional properties.
  - **`inputs`** *(string, required)*: Path to input configuration table, relative to working directory. See (inputs.md) for more detail.
  - **`indicators`** *(string, required)*: Path to indicator configuration table, relative to working directory. See (indicators.md) for more detail.
  - **`scenarios`** *(string, required)*: Path to scenario configuration table, relative to working directory. See (scenarios.md) for more detail.
  - **`periods`** *(string, required)*: Path to period configuration table, relative to working directory. See (periods.md) for more detail.
  - **`seasons`** *(string, required)*: Path to season configuration table, relative to working directory. See (seasons.md) for more detail.
- **`notebooks`**: List of paths to Jupyter notebooks that should be compiled in the pipeline. Multiple notebooks can be specified using square-braces e.g. ['foo','bar']. If empty, no notebooks will be built.
  - **One of**
    - *['string', 'null']*
    - *array*
      - **Items** *(string)*
- **`arealstats`** *(object)*: Cannot contain additional properties.
  - **`calcForMembers`** *(boolean, required)*: Should the areal statistics be calculated for the individual ensemble members as well as for the entire ensemble. `true` or `false`.
- **`dirs`** *(object)*: Directories for storing output and intermediate files. Can be specified as either absolute paths, or relative to the working directory. See the [KAPy concepts](../KAPy_concepts.md) documentation for a more detailed description of these items. Cannot contain additional properties.
  - **`primVars`** *(string, required)*: Directory for storing primary variables.
  - **`bc`** *(string, required)*: Directory for storing bias-corrected variables.
  - **`indicators`** *(string, required)*: Directory for storing indicators variables.
  - **`regridded`** *(string, required)*: Directory for storing indicators regridded to a common grid.
  - **`ensstats`** *(string, required)*: Directory for storing enssemble statistics.
  - **`arealstats`** *(string, required)*: Directory for storing statistics calculated over areas.
  - **`notebooks`** *(string, required)*: Directory for storing compiled Jupyter notebooks.
- **`ensembles`** *(object)*: Specify the percentiles [0-100] calculated from the ensemble. We allow three values, corresponding to the upper and lower confidence limits, and the central value. Cannot contain additional properties.
  - **`upperPercentile`** *(integer, required)*: Exclusive minimum: `0`. Exclusive maximum: `100`.
  - **`centralPercentile`** *(integer, required)*: Exclusive minimum: `0`. Exclusive maximum: `100`.
  - **`lowerPercentile`** *(integer, required)*: Exclusive minimum: `0`. Exclusive maximum: `100`.
- **`primVars`** *(object)*: Configuration options relating to the primary variables. Cannot contain additional properties.
  - **`storeAsNetCDF`** *(boolean, required)*: Should the primary variables be stored as NetCDF files (`true`) or written as pickled versions of the internal xarray objects (`false`). The former work with intermediate tools, the later saves disk space.
