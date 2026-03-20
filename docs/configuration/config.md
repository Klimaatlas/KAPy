# KAPy configuration options

*Configuration schema for KAPy configuration objects. These configurations are usually stored in the `config.yaml` file.*

## Properties

- <a id="properties/configurationTables"></a>**`configurationTables`**: Paths to configuration tables. See the documentation for each table separately. Cannot contain additional properties.
  - <a id="properties/configurationTables/properties/inputs"></a>**`inputs`** *(string, required)*: Path to input configuration table, relative to working directory. See [inputs.md](inputs.md) for more detail. Required table.
  - <a id="properties/configurationTables/properties/secondaryVars"></a>**`secondaryVars`** *(string or null, required)*: Path to configuration table for secondary variables, relative to working directory. See [derivedVars.md](derivedVars.md) for more details. Optional - if set to '' or undefined, no secondary variables will be generated.
  - <a id="properties/configurationTables/properties/biasAdjustment"></a>**`biasAdjustment`** *(string or null, required)*: Path to bias adjustment configuration table, relative to working directory. See [biasAdjustment.md](biasAdjustment.md) for more detail. Optional - if set to '' or undefined, no bias adjustment will be performed.
  - <a id="properties/configurationTables/properties/tertiaryVars"></a>**`tertiaryVars`** *(string or null, required)*: Path to configuration table for tertiary variables, relative to working directory. See [derivedVars.md](derivedVars.md) for more details. Optional - if set to '' or undefined, no tertiary variables will be generated.
  - <a id="properties/configurationTables/properties/indicators"></a>**`indicators`** *(string or null, required)*: Path to indicator configuration table, relative to working directory. See [indicators.md](indicators.md) for more detail. Optional - if set to '' or undefined, no indicators will be generated.
  - <a id="properties/configurationTables/properties/periods"></a>**`periods`** *(string, required)*: Path to period configuration table, relative to working directory. See [periods.md](periods.md) for more detail. Required table.
  - <a id="properties/configurationTables/properties/seasons"></a>**`seasons`** *(string, required)*: Path to season configuration table, relative to working directory. See [seasons.md](seasons.md) for more detail. Required table.
- <a id="properties/dirs"></a>**`dirs`** *(object, required)*: Directories for storing output and intermediate files. Can be specified as either absolute paths, or relative to the working directory. See the [KAPy concepts](../KAPy_concepts.md) documentation for a more detailed description of these items. Cannot contain additional properties.
  - <a id="properties/dirs/properties/primaryVariables"></a>**`primaryVariables`** *(string, required)*: Directory for storing primary variables.
  - <a id="properties/dirs/properties/secondaryVariables"></a>**`secondaryVariables`** *(string, required)*: Directory for storing secondary variables.
  - <a id="properties/dirs/properties/biasAdjustment"></a>**`biasAdjustment`** *(string, required)*: Directory for storing bias-adjusted variables.
  - <a id="properties/dirs/properties/tertiaryVariables"></a>**`tertiaryVariables`** *(string, required)*: Directory for storing tertiary variables.
  - <a id="properties/dirs/properties/indicators"></a>**`indicators`** *(string, required)*: Directory for storing indicators.
  - <a id="properties/dirs/properties/regridded"></a>**`regridded`** *(string, required)*: Directory for storing indicators regridded to a common grid.
  - <a id="properties/dirs/properties/ensstats"></a>**`ensstats`** *(string, required)*: Directory for storing ensemble statistics.
  - <a id="properties/dirs/properties/arealstats"></a>**`arealstats`** *(string, required)*: Directory for storing statistics calculated over areas.
  - <a id="properties/dirs/properties/outputs"></a>**`outputs`** *(string, required)*: Directory for storing output files and databases. Plots are stored in the ./plots subdirectory.
  - <a id="properties/dirs/properties/tempDir"></a>**`tempDir`** *(string, required)*: Temporary directory to be used for scratch files.
- <a id="properties/outputs"></a>**`outputs`** *(object, required)*: Paths for writing output files. Cannot contain additional properties.
  - <a id="properties/outputs/properties/ensembleStatisticsCSV"></a>**`ensembleStatisticsCSV`** *(string, required)*: Path to .csv file combining all areal statistics summarised across the entire ensemble.
  - <a id="properties/outputs/properties/ensembleMembersCSV"></a>**`ensembleMembersCSV`** *(string, required)*: Path to .csv file combining the  areal statistics for each individual ensemble member.
  - <a id="properties/outputs/properties/database"></a>**`database`** *(string, required)*: Path to SQLite database / Geopackage merging all outputs from the pipeline.
- <a id="properties/arealstats"></a>**`arealstats`** *(object, required)*: Cannot contain additional properties.
  - <a id="properties/arealstats/properties/useAreaWeighting"></a>**`useAreaWeighting`** *(boolean, required)*: Use area-weighting when calculating averages over a polygon or area. Nearly all climate data is presented on grids where the area of the pixels is not constant, but changes in space - for example, on a regular lat-lon grid, the pixels get smaller towards the poles. When this option is configured, the CDO `gridarea` operator is used to calculate the area of each cell, and weightings applied to the calculation of area statistics accordingly. Requires that CDO can calculate the cell area - otherwise, it is recommended to disable this option manually.
  - <a id="properties/arealstats/properties/shapefile"></a>**`shapefile`** *(string or null, required)*: Path to shapefile to be used for defining areas. When the path is undefined, averages are calculated across the entire domain. The path should point to the .shp file.
- <a id="properties/cutouts"></a>**`cutouts`**: Configures spatial-subsetting (cutting-out) of the input data.
  - **One of**
    - <a id="properties/cutouts/oneOf/0"></a>*object*: **none**. Omit the cutout step. All available data in the input files is processed. Cannot contain additional properties.
      - <a id="properties/cutouts/oneOf/0/properties/method"></a>**`method`** *(string, required)*: Must be one of: "none".
    - <a id="properties/cutouts/oneOf/1"></a>*object*: **lonlatbox**. Use the `sellonlatbox`operator from cdo to do the subsetting. Details of this operator can be found in the CDO documentation. Cannot contain additional properties.
      - <a id="properties/cutouts/oneOf/1/properties/method"></a>**`method`** *(string, required)*: Must be one of: "lonlatbox".
      - <a id="properties/cutouts/oneOf/1/properties/xmin"></a>**`xmin`** *(number, required)*: Western boundary of cutout box.
      - <a id="properties/cutouts/oneOf/1/properties/xmax"></a>**`xmax`** *(number, required)*: Eastern boundary of cutout box.
      - <a id="properties/cutouts/oneOf/1/properties/ymin"></a>**`ymin`** *(number, required)*: Southern boundary of cutout box.
      - <a id="properties/cutouts/oneOf/1/properties/ymax"></a>**`ymax`** *(number, required)*: Northern boundary of cutout box.
- <a id="properties/ensembles"></a>**`ensembles`** *(object, required)*: Parameters to control the calculation of ensemble statistics. Cannot contain additional properties.
  - <a id="properties/ensembles/properties/percentiles"></a>**`percentiles`** *(array, required)*: Specify the percentiles [0-100] calculated from the ensemble. We allow any number of values. Values of 0 and 100 indicate the maximum / minimum values in the ensemble. Length must be at least 1. Items must be unique.
    - <a id="properties/ensembles/properties/percentiles/items"></a>**Items** *(integer)*: Minimum: `0`. Maximum: `100`.
  - <a id="properties/ensembles/properties/method"></a>**`method`** *(string, required)*: Specifies the interpolation method to use when the desired quantile lies between two data points. Default value is 'linear'. String is supplied to the `method` argument of `xarray.dataset.quantile()` - see the documentation there for details. Must be one of: "inverted_cdf", "averaged_inverted_cdf", "closest_observation", "interpolated_inverted_cdf", "hazen", "weibull", "linear", "median_unbiased", "normal_unbiased", "lower", "higher", "midpoint", or "nearest".
- <a id="properties/outputGrid"></a>**`outputGrid`** *(object, required)*: Defines the common output grid onto which KAPy interpolates all indicators before calculating ensemble statistics. Can be disabled by setting `templateType` to `none`. . Cannot contain additional properties.
  - <a id="properties/outputGrid/properties/templateType"></a>**`templateType`** *(string, required)*: Type of template to use to specify the output grid. Selecting `none` will disable regridding. Selecting `file` will use an existing NetCDF file as the template. `cdo` uses a CDO grid descriptor file as the template. Must be one of: "none", "cdo", or "file".
  - <a id="properties/outputGrid/properties/gridName"></a>**`gridName`** *(string, required)*: String giving the name of the grid to be used in regridding filenames.
  - <a id="properties/outputGrid/properties/method"></a>**`method`** *(string, required)*: Method used by the xESMF Regridder function to do the regridding. See documentaiton for xESMF for details. Must be one of: "bilinear", "conservative", "conservative_normed", "patch", "nearest_s2d", or "nearest_d2s".
  - <a id="properties/outputGrid/properties/path"></a>**`path`** *(string, required)*: Path to the file to be used as a template, in the case of a `file` templateType, or the cdo grid descriptor, in the case of `cdo` templateType.
