# KAPy configuration options

*Configuration schema for KAPy configuration objects. These configurations are usually stored in the `config.yaml` file.*

## Properties

- <a id="properties/configuration_tables"></a>**`configuration_tables`**: Paths to configuration tables. See the documentation for each table separately. Cannot contain additional properties.
  - <a id="properties/configuration_tables/properties/inputs"></a>**`inputs`** *(string, required)*: Path to input configuration table, relative to working directory. See [inputs.md](inputs.md) for more detail. Required table.
  - <a id="properties/configuration_tables/properties/secondary_variables"></a>**`secondary_variables`** *(string or null, required)*: Path to configuration table for secondary variables, relative to working directory. See [derivedVars.md](derivedVars.md) for more details. Optional - if set to '' or undefined, no secondary variables will be generated.
  - <a id="properties/configuration_tables/properties/bias_adjustment"></a>**`bias_adjustment`** *(string or null, required)*: Path to bias adjustment configuration table, relative to working directory. See [biasAdjustment.md](biasAdjustment.md) for more detail. Optional - if set to '' or undefined, no bias adjustment will be performed.
  - <a id="properties/configuration_tables/properties/tertiary_variables"></a>**`tertiary_variables`** *(string or null, required)*: Path to configuration table for tertiary variables, relative to working directory. See [derivedVars.md](derivedVars.md) for more details. Optional - if set to '' or undefined, no tertiary variables will be generated.
  - <a id="properties/configuration_tables/properties/indicators"></a>**`indicators`** *(string or null, required)*: Path to indicator configuration table, relative to working directory. See [indicators.md](indicators.md) for more detail. Optional - if set to '' or undefined, no indicators will be generated.
  - <a id="properties/configuration_tables/properties/periods"></a>**`periods`** *(string, required)*: Path to period configuration table, relative to working directory. See [periods.md](periods.md) for more detail. Required table.
  - <a id="properties/configuration_tables/properties/seasons"></a>**`seasons`** *(string, required)*: Path to season configuration table, relative to working directory. See [seasons.md](seasons.md) for more detail. Required table.
- <a id="properties/output_directory"></a>**`output_directory`** *(string, required)*: Path for writing output files.
- <a id="properties/areal_statistics"></a>**`areal_statistics`** *(object, required)*: Cannot contain additional properties.
  - <a id="properties/areal_statistics/properties/use_area_weighting"></a>**`use_area_weighting`** *(boolean, required)*: Use area-weighting when calculating averages over a polygon or area. Nearly all climate data is presented on grids where the area of the pixels is not constant, but changes in space - for example, on a regular lat-lon grid, the pixels get smaller towards the poles. When this option is configured, the CDO `gridarea` operator is used to calculate the area of each cell, and weightings applied to the calculation of area statistics accordingly. Requires that CDO can calculate the cell area - otherwise, it is recommended to disable this option manually.
  - <a id="properties/areal_statistics/properties/shapefile"></a>**`shapefile`** *(string or null, required)*: Path to shapefile to be used for defining areas. When the path is undefined, averages are calculated across the entire domain. The path should point to the .shp file.
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
- <a id="properties/output_grid"></a>**`output_grid`** *(object, required)*: Defines the common output grid onto which KAPy interpolates all indicators before calculating ensemble statistics. Can be disabled by setting `templateType` to `none`. Cannot contain additional properties.
  - <a id="properties/output_grid/properties/template_type"></a>**`template_type`** *(string, required)*: Type of template to use to specify the output grid. Selecting `none` will disable regridding. Selecting `file` will use an existing NetCDF file as the template. `cdo` uses a CDO grid descriptor file as the template. Must be one of: "none", "cdo", or "file".
  - <a id="properties/output_grid/properties/grid_name"></a>**`grid_name`** *(string)*: String giving the name of the grid to be used in regridding filenames.
  - <a id="properties/output_grid/properties/method"></a>**`method`** *(string)*: Method used by the xESMF Regridder function to do the regridding. See documentaiton for xESMF for details. Must be one of: "bilinear", "conservative", "conservative_normed", "patch", "nearest_s2d", or "nearest_d2s".
  - <a id="properties/output_grid/properties/path"></a>**`path`** *(string)*: Path to the file to be used as a template, in the case of a `file` templateType, or the cdo grid descriptor, in the case of `cdo` templateType.
- <a id="properties/dask_resources"></a>**`dask_resources`** *(string or null, required)*: Paths to dask resource specification type.
