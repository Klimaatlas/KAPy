# KAPy Concepts

KAPy is intented to be a generic and modular tool for the production of climate services. The tool can be used in its entirety, or individual modules can be used separately - workflows that merge KAPy with other tools (e.g. hydrological modelling) and flip between them, can also be envisaged, and are allowed for. However, given the very varied and tailored nature of climate services, it is unlikely that KAPy will be able to meet all needs. The structure of KAPy is shaped to a large degree by the needs of the national climate atlases of both Ghana and Denmark, but the intention is to take a highly generic approach to this work, to enable the tool to be applied in other settings.

In this document we describe the core concepts and definitions that KAPy is built up around.

## Some defintions

To start with a few key definitions around the types of data that we can potentially deal with
* *Climate variable* We refer to any output produced directly by a climate model (either global or regional) as a "climate variable". Example include temperature, maximum temperature, precipitation etc.
* *Climate indicator* Climate variables can then be translated into climate indicators via a post-processing scheme. Examples include annual mean temperature, frequency of extreme rain events, and drought indices. The information delivered by a climate service, and that commonly serves as the basis for further decision decision making, is can generally be described as an "indicator". Indicators can be calculated from both climate variables and derived variables.
* *Derived variables* Derived climate variables sit between variables and indicators, often representing an intermediate post-processing step that is still too abstract to be used as the basis for decision making. For example, the Canadian Fire Weather Index (FWI) is not directly available from climate models, but rather is a complex function of temperature, precipitation, wind and humidity. However, FWI is often difficult to interpret directly, requiring the use of indicators e.g. number of days with extreme fire danger. 

KAPy also has a number of key user-configurable concepts that shape the way the analysis is performed.
* *Datasets* form a single time-series of a climate or derived variable that can be used as the basis for calculating indicators. Datasets can often aggregate across multiple "experiments" in CMIP terminology, e.g. joining "hist" and "rcp26" into one timeseries. However, the requirement for only one timeseries per dataset means that e.g. "rcp26" and "rcp85" cannot be represented in the same dataset, as they have overlapping timeseries - instead, these are best represented as separate datasets.
* *Periods* are discrete time windows over which indicators are calculated and/or averaged. Multiple periods can be defined in a configuration, and can be overlapping. Minimum period length is 1 year.
* *Seasons* represent a grouping of one or more months over which indicators are calculated e.g. winter precipitation. Multiple seasons are permitted in a configuration, and they need not be mutually exclusive.


## Workflow

The KAPy workflow involves a set of discrete steps to process climate data, covering the necessary steps to go from online climate databases to the production of climate indicators and output files in relevant formats. These steps are described here, with reference to the corresponding Snakemake targets. 

* Data acquisition
  * Data availabe in remote databases (e.g. ESGF, potentially Copernicus CDS in the future) is identified based on specifications in `config.yaml` and downloaded. In cases where the data is already locally available, this step can be skipped.
  * `search` -  Queries online databases to find matching files
  * `URLs` - Retrieve the URL location of the files identified in `search`
  * `download` - Retrieves each individual file and stores it locally. Where supported by the remote server, spatial subsetting defined in `config.yaml`, is applied prior to downloading.
  * `download_status`- Produces a .html notebook comparing the file "wishlist" with what is actually available. Useful for keeping track of the download status.

* Collate datasets
  * Individual files in our local database are grouped into Xarray "dataset" objects that form the basis of all subsequent indicator calculations
 * `datasets` builds all datasets.

* Derived variables
  * Production of some derived variables (e.g. FWI) will be  supported in KAPy via the xclim toolbox. However, this feature is not currently implemented. 

* Indicator calculation
  * Indicators are calculated for each dataset. Each individual 
  * `indicators` builds all indicators
  * Individual indicators can be built by using their id code as a target e.g. `i101`

* Regridding
  * Regridding is a precursor to ensemble statistics, and is often necessary to ensure that all models are on entirely identical grid
  * `regrid` regrids all files to the common grid defined in `config.yaml`

* Ensemble statistics
  * Indicators on a common grid can then be merged into a single object and ensemble statistics (e.g. median, mean 10th percentile, 90th percentile) calculated
  * `ensstats` calculates the ensemble statistics for all indicators.

* Areal statistics
  * Indicator statistics are calculated for all polygons defined in `config.yaml`. 
  * Currently not implemented.

* Outputs
  * Produce output files
  * `notebooks` produces an overview noteProduce output files
  * `notebooks` produces an overview notebook of all indicators

