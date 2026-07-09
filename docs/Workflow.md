# KAPy - Snakemake workflow

The KAPy workflow involves a set of discrete steps to process climate data, covering the necessary steps to go from online climate databases to the production of climate indicators and output files in relevant formats. These steps are described here, with reference to the corresponding Snakemake targets. 

* `primaryVars` : Primary variables 
  * Individual files in our local database are grouped into "dataset" objects that form the basis of all subsequent calculations. 
  
* `secondaryVars` : Secondary variables  
  * Additional variables are generated based on new combinations or further processing of primary variables

* `biasAdjustment` : Bias adjustment variables
  * Generates new datasets by applying bias adjustment techniques to the primary and secondary variables.
  
* `indicators` : Indicator calculation
  * Indicators are calculated for each dataset. 
  * Individual indicators can be built by using their id code as a target e.g. `101`

* `regrid` : Regridded files
  * Indicators are regridded to a common grid

* `ensstats` : Ensemble statistics
  * Indicators on a common grid can then be merged into a single object and ensemble statistics (e.g. median, mean 10th percentile, 90th percentile) calculated

* `arealstats` : Areal statistics
  * Indicator statistics are calculated for all polygons area defined in `config.yaml`. 
 
* `all` : Make everything
  * Produce all outputs.
  * The default target - if no target is defined when calling snakemake, everything will be produced.

