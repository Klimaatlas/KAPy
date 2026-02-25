# KAPy configuration options

*Configuration schema for KAPy configuration objects. These configurations are usually stored in the `config.yaml` file.*

## Properties

- **`configurationTables`**: Paths to configuration tables. See the documentation for each table separately. Cannot contain additional properties.
  - **`inputs`** *(string, required)*: Path to input configuration table, relative to working directory. See [inputs.md](inputs.md) for more detail. Required table.
  - **`secondaryVars`** *(string, required)*: Path to configuration table for secondary variables, relative to working directory. See [derivedVars.md](derivedVars.md) for more details. Optional - if set to '', no secondary variables will be generated.
  - **`biasAdjustment`** *(string, required)*: Path to bias adjustment configuration table, relative to working directory. See [biasAdjustment.md](biasAdjustment.md) for more detail. Optional - if set to '', no bias adjustment will be performed.
  - **`tertiaryVars`** *(string, required)*: Path to configuration table for tertiary variables, relative to working directory. See [derivedVars.md](derivedVars.md) for more details. Optional - if set to '', no tertiary variables will be generated.
  - **`indicators`** *(string, required)*: Path to indicator configuration table, relative to working directory. See [indicators.md](indicators.md) for more detail. Optional - if set to '', no indicators will be generated.
  - **`periods`** *(string, required)*: Path to period configuration table, relative to working directory. See [periods.md](periods.md) for more detail. Required table.
  - **`seasons`** *(string, required)*: Path to season configuration table, relative to working directory. See [seasons.md](seasons.md) for more detail. Required table.
- **`dirs`** *(object, required)*: Directories for storing output and intermediate files. Can be specified as either absolute paths, or relative to the working directory. See the [KAPy concepts](../KAPy_concepts.md) documentation for a more detailed description of these items. Cannot contain additional properties.
  - **`primaryVariables`** *(string, required)*: Directory for storing primary variables.
  - **`secondaryVariables`** *(string, required)*: Directory for storing secondary variables.
  - **`biasAdjustment`** *(string, required)*: Directory for storing bias adjusted variables.
  - **`tertiaryVariables`** *(string, required)*: Directory for storing tertiary variables.
  - **`indicators`** *(string, required)*: Directory for storing indicators.
  - **`regridded`** *(string, required)*: Directory for storing indicators regridded to a common grid.
  - **`ensstats`** *(string, required)*: Directory for storing ensemble statistics.
  - **`arealstats`** *(string, required)*: Directory for storing statistics calculated over areas.
  - **`outputs`** *(string, required)*: Directory for storing output files and databases. Plots are stored in the ./plots subdirectory.
  - **`tempDir`** *(string, required)*: Temporary directory to be used for scratch files.
- **`outputs`** *(object, required)*: Paths for writing output files. Cannot contain additional properties.
  - **`ensembleStatisticsCSV`** *(string, required)*: Path to .csv file combining all areal statistics summarised across the entire ensemble.
  - **`ensembleMembersCSV`** *(string, required)*: Path to .csv file combining the  areal statistics for each individual ensemble member.
  - **`database`** *(string, required)*: Path to SQLite database merging all outputs from the pipeline.
- **`arealstats`** *(object, required)*: Cannot contain additional properties.
  - **`useAreaWeighting`** *(boolean, required)*: Use area-weighting when calculating averages over a polygon or area. Nearly all climate data is presented on grids where the area of the pixels is not constant, but changes in space - for example, on a regular lat-lon grid, the pixels get smaller towards the poles. When this option is configured, the CDO `gridarea` operator is used to calculate the area of each cell, and weightings applied to the calculation of area statistics accordingly. Requires that CDO can calculate the cell area - otherwise, it is recommended to disable this option manually.
  - **`shapefile`** *(['string', 'null'], required)*: Path to shapefile to be used for defining areas. When the path is undefined, averages are calculated across the entire domain. The path should point to the .shp file.
  - **`idColumn`** *(['string', 'null'], required)*: Name of the column in the above shapefile to be used as a unique identifier code for the area.
- **`cutouts`**: Configures spatial-subsetting (cutting-out) of the input data.
  - **One of**
    - *object*: **none**. Omit the cutout step. All available data in the input files is processed. Cannot contain additional properties.
      - **`method`** *(string, required)*: Must be one of: `["none"]`.
    - *object*: **lonlatbox**. Use the `sellonlatbox`operator from cdo to do the subsetting. Details of this operator can be found in the CDO documentation. Cannot contain additional properties.
      - **`method`** *(string, required)*: Must be one of: `["lonlatbox"]`.
      - **`xmin`** *(number, required)*: Western boundary of cutout box.
      - **`xmax`** *(number, required)*: Eastern boundary of cutout box.
      - **`ymin`** *(number, required)*: Southern boundary of cutout box.
      - **`ymax`** *(number, required)*: Northern boundary of cutout box.
- **`ensembles`** *(object, required)*: Specify the percentiles [0-100] calculated from the ensemble. We allow three values, corresponding to the upper and lower confidence limits, and the central value. Cannot contain additional properties.
  - **`upperPercentile`** *(integer, required)*: Exclusive minimum: `0`. Exclusive maximum: `100`.
  - **`centralPercentile`** *(integer, required)*: Exclusive minimum: `0`. Exclusive maximum: `100`.
  - **`lowerPercentile`** *(integer, required)*: Exclusive minimum: `0`. Exclusive maximum: `100`.
- **`outputGrid`** *(object, required)*: Defines the common output grid onto which KAPy interpolates all indicators before calculating ensemble statistics. Can be disabled by setting `templateType` to `none`. . Cannot contain additional properties.
  - **`templateType`** *(string, required)*: Type of template to use to specify the output grid. Selecting `none` will disable regridding. Selecting `file` will use an existing NetCDF file as the template. `cdo` uses a CDO grid descriptor file as the template. Must be one of: `["none", "cdo", "file"]`.
  - **`gridName`** *(string, required)*: String giving the name of the grid to be used in regridding filenames.
  - **`method`** *(string, required)*: Method used by the xESMF Regridder function to do the regridding. See documentaiton for xESMF for details. Must be one of: `["bilinear", "conservative", "conservative_normed", "patch", "nearest_s2d", "nearest_d2s"]`.
  - **`path`** *(string, required)*: Path to the file to be used as a template, in the case of a `file` templateType, or the cdo grid descriptor, in the case of `cdo` templateType.
- **`processing`** *(object, required)*: Cannot contain additional properties.
  - **`picklePrimaryVariables`** *(boolean, required)*: Should the the primary variables be stored as 'pickled' xarray objects (`True`) or written out to disk as NetCDF files (`False`).
