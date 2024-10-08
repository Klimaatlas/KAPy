# KAPy configuration options

*Configuration schema for KAPy configuration objects. These configurations are usually stored in the `config.yaml` file.*

## Properties

- **`configurationTables`**: Paths to configuration tables. See the documentation for each table separately. Cannot contain additional properties.
  - **`inputs`** *(string, required)*: Path to input configuration table, relative to working directory. See [inputs.md](inputs.md) for more detail.
  - **`secondaryVars`** *(string)*: Path to configuration table for secondary variables, relative to working directory. See [derivedVars.md](derivedVars.md) for more details. Optional - if omitted, no secondary variables will be generated.
  - **`indicators`** *(string, required)*: Path to indicator configuration table, relative to working directory. See [indicators.md](indicators.md) for more detail.
  - **`periods`** *(string, required)*: Path to period configuration table, relative to working directory. See [periods.md](periods.md) for more detail.
  - **`seasons`** *(string, required)*: Path to season configuration table, relative to working directory. See [seasons.md](seasons.md) for more detail.
- **`dirs`** *(object)*: Directories for storing output and intermediate files. Can be specified as either absolute paths, or relative to the working directory. See the [KAPy concepts](../KAPy_concepts.md) documentation for a more detailed description of these items. Cannot contain additional properties.
  - **`variables`** *(string, required)*: Directory for storing variables.
  - **`indicators`** *(string, required)*: Directory for storing indicators.
  - **`regridded`** *(string, required)*: Directory for storing indicators regridded to a common grid.
  - **`ensstats`** *(string, required)*: Directory for storing ensemble statistics.
  - **`arealstats`** *(string, required)*: Directory for storing statistics calculated over areas.
  - **`plots`** *(string, required)*: Directory for storing output plots.
- **`arealstats`** *(object)*: Cannot contain additional properties.
  - **`calcForMembers`** *(boolean, required)*: Should the areal statistics be calculated for the individual ensemble members as well as for the entire ensemble. `true` or `false`.
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
- **`ensembles`** *(object)*: Specify the percentiles [0-100] calculated from the ensemble. We allow three values, corresponding to the upper and lower confidence limits, and the central value. Cannot contain additional properties.
  - **`upperPercentile`** *(integer, required)*: Exclusive minimum: `0`. Exclusive maximum: `100`.
  - **`centralPercentile`** *(integer, required)*: Exclusive minimum: `0`. Exclusive maximum: `100`.
  - **`lowerPercentile`** *(integer, required)*: Exclusive minimum: `0`. Exclusive maximum: `100`.
- **`outputGrid`**: Defines the common output grid onto which KAPy interpolates all indicators before calculating ensemble statistics. Multiple approaches to regridding can be configured, as described below.
  - **One of**
    - *object*: **none**. Omit the regridding step. Assumes that all files within an input type are on the same grid, which will be used as the output grid. Cannot contain additional properties.
      - **`regriddingEngine`** *(string, required)*: Must be one of: `["none"]`.
    - *object*: **cdo**. Use the Climate Data Operators to do the regridding. For more information, see the CDO website, https://code.mpimet.mpg.de/projects/cdo. Installation of CDO is handled behind the scenes by conda as part of the KAPy environment setup - be aware that this may result in a different version of CDO being used to what you have by default. In the current configuration we default to bilinear interpolation (`remapbil`). If other operators are required, please file a feature request in GitHub. Cannot contain additional properties.
      - **`regriddingEngine`** *(string, required)*: Must be one of: `["cdo"]`.
      - **`gridName`** *(string, required)*: String giving the name of the grid to be used in regridding filenames.
      - **`cdoGriddes`** *(string, required)*: Path to CDO grid descriptor, specifying the output grid. For more information see the CDO documentation, specifically section 1.5 about horizontal grids, section 2.12 about interpolation and Appendix D for examples of grid descriptors.
- **`processing`** *(object)*: Cannot contain additional properties.
  - **`picklePrimaryVariables`** *(boolean, required)*: Should the the primary variables be stored as 'pickled' xarray objects (`True`) or written out to disk as NetCDF files (`False`).
