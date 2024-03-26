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
- **`notebooks`**: Jupyter notebooks that should be compiled in the pipeline. Multiple configuration options are possible.
  - **One of**
    - *null*: No notebooks to be built.
    - *string*: Path to a single notebook to build.
    - *array*: Paths to multiple notebooks, specified as a list using square-braces e.g. ['foo','bar'].
      - **Items** *(string)*
- **`outputGrid`**: Defines the common output grid onto which KAPy interpolates all indicators before calculating ensemble statistics. Multiple approaches to regridding can be configured, as described below.
  - **One of**
    - *object*: Omit the regridding step. Assumes that all files within an input type are on the same grid, which will be used as the output grid. Cannot contain additional properties.
      - **`regriddingEngine`** *(string, required)*: Must be one of: `["None"]`.
    - *object*: Perform regridding using the xesmf package. See also the [documentation for xesmf](https://xesmf.readthedocs.io/) for a more detailed description of specific configurations. Cannot contain additional properties.
      - **`regriddingEngine`** *(string, required)*: Must be one of: `["xesmf"]`.
      - **`interpMethod`** *(string, required)*: The `method` argument to `xesmf.frontend.Regridder` that chooses the regridding method. See xesmf documentation for a description of options. Must be one of: `["bilinear", "conservative", "conservative_normed", "patch", "nearest_s2d", "nearest_d2s"]`.
      - **`extrapMethod`** *(string, required)*: The `extrap_method` argument to `xesmf.frontend.Regridder` that chooses the extrapolation method. See xesmf documentation for a description of options. Must be one of: `["inverse_dist", "nearest_s2d", null]`.
      - **`xname`** *(string, required)*: Name of x axis in output files .
      - **`xunits`** *(string, required)*: Units of the y axis in output files .
      - **`xmin`** *(number, required)*: Western boundary of output grid. .
      - **`xmax`** *(number, required)*: Eastern boundary of output grid. .
      - **`dx`** *(number, required)*: Spacing between nodes in the x direction .
      - **`yname`** *(string, required)*: Name of y axis in output files .
      - **`yunits`** *(string, required)*: Units of the y axis in output files .
      - **`ymin`** *(number, required)*: Southern boundary of output grid. .
      - **`ymax`** *(number, required)*: Northern boundary of output grid. .
      - **`dy`** *(number, required)*: Spacing between nodes in the y direction .
- **`arealstats`** *(object)*: Cannot contain additional properties.
  - **`calcForMembers`** *(boolean, required)*: Should the areal statistics be calculated for the individual ensemble members as well as for the entire ensemble. `true` or `false`.
- **`dirs`** *(object)*: Directories for storing output and intermediate files. Can be specified as either absolute paths, or relative to the working directory. See the [KAPy concepts](../KAPy_concepts.md) documentation for a more detailed description of these items. Cannot contain additional properties.
  - **`primVars`** *(string, required)*: Directory for storing primary variables.
  - **`secVars`** *(string)*: Directory for storing secondary variables.
  - **`bc`** *(string, required)*: Directory for storing bias-corrected variables.
  - **`tertVars`** *(string)*: Directory for storing teriary variables.
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
