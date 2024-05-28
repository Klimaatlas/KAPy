# KAPy Concepts

KAPy is intented to be a generic and modular tool for the production of climate services. The tool can be used in its entirety, or individual modules can be used separately - workflows that merge KAPy with other tools (e.g. hydrological modelling) and flip between them, can also be envisaged, and are allowed for. However, given the very varied and tailored nature of climate services, it is unlikely that KAPy will be able to meet all needs. The structure of KAPy is shaped to a large degree by the needs of the national climate atlases of both Ghana and Denmark, but the intention is to take a highly generic approach to this work, to enable the tool to be applied in other settings.

In this document we describe the core concepts and definitions that KAPy is built up around.

## Some defintions

To start with a few key definitions around the types of data that we can potentially deal with
* *Climate variable* We refer to gridded climate data in its native time resolution as a "climate variable". This can include the output produced directly by a climate model (either global or regional) or observations. It can also included derived variables, that are produced as a combination of other variables from the same data source, or in interaction with other data sources (e.g. as in bias correction). Examples include temperature, maximum temperature, precipitation etc.
* *Climate indicator* Climate variables can then be translated into climate indicators via a processing scheme involving the generation of some form of summary statistic (e.g. a mean) over time. Examples include annual mean temperature, frequency of extreme rain events, and drought indices. 

The key distinction between a variable and an indicator is the act of time-averaging. Climate variables  have a higher time resolution (e.g. months, days or hours) than the corresponding indicators (e.g. annual averages, 30 year averages). The information delivered by a climate service, and that commonly serves as the basis for further decision decision making, is most commonly in the form of "indicators".

We can add further gradations of climate variables that recognise how much they have been modified from the original input dataset. The taxonomy used here is:
* *Primary variables (PV)* are those directly available in the input data sources. A few minor reshuffling steps (e.g. cutting out the region of interest, renaming variables to a standard taxnonomy) may have occured, and  model experiments may be merged (e.g. merging the "historical" and "rcp85" experiments into one continuous time series). However, the data that remains is untouched relative to the source files. Examples include daily maximum temperature and precipitation.
* *Secondary variables (SV)* are modifications or combinations of the primary variables, often representing an intermediate post-processing step. For example, the Canadian Fire Weather Index (FWI) is not directly available from climate models, but rather is a complex function of the primary variables temperature, precipitation, wind and humidity. 
* *Bias corrected variables (BCV)* have had statistical aspects (e.g. mean, variance) of their distribution modified to target a target "truth" distribution (e.g. observations). They are in a form of secondary variable, but given their unique nature (and importance) in the climate service value chain, we name them explicitly.
* *Tertiary variables (TV)* are a second form of derived variables based on bias-corrected (rather than primary) variables. In the case of the fire weather index above, the FWI could equally be calculated based on bias-corrected versions of temperature, precipitation, wind and humidity. 

As the example with FWI shows, there are multiple routes to calculating some derived variables. It is a goal of KAPy to provide sufficient flexibility that the user is able to make decisions about what is the most appropriate route, rather than the software presaging a particular workflow.

We also consider two gradations of climate indicators:
* *Primary Indicators (PI)* are the "raw" indicators and can be calculated from any of the four types of climate variables (PV, SV, BCV, TV).
* *Bias corrected indicators (BCI)* apply a subsequent bias-correction step to the primary indicators.

An example of where bias-corrected indicators come into play is in projections of return periods of e.g. extreme rainfall. As used in the Danish National Climate Atlas, *Klimaatlas*, return periods are first calculated directly from primary variables from both climate model and observational datasets - a time-averaging process, making the outputs indicators in this taxonomy. These primary indicators are then bias-corrected to produce the bias-corrected indicators that are actually presented in the climate service.

KAPy also has a number of key user-configurable concepts that shape the way the analysis is performed.
* *Datasets* form a single time-series of a climate or derived variable that can be used as the basis for calculating indicators. Datasets can often aggregate across multiple "experiments" in CMIP terminology, e.g. joining "hist" and "rcp26" into one timeseries. However, the requirement for only one timeseries per dataset means that e.g. "rcp26" and "rcp85" cannot be represented in the same dataset, as they have overlapping timeseries - instead, these are best represented as separate datasets.
* *Periods* are discrete time windows over which indicators are calculated and/or averaged. Multiple periods can be defined in a configuration, and can be overlapping. Minimum period length is 1 year.
* *Seasons* represent a grouping of one or more months over which indicators are calculated e.g. winter precipitation. Multiple seasons are permitted in a configuration, and they need not be mutually exclusive.


## Workflow

The KAPy workflow involves a set of discrete steps to process climate data, covering the necessary steps to go from online climate databases to the production of climate indicators and output files in relevant formats. These steps are described here, with reference to the corresponding Snakemake targets. 

* `primaryVars` : Primary variables 
  * Individual files in our local database are grouped into "dataset" objects that form the basis of all subsequent calculations. 
  
* `secondaryVars` : Secondary variables  
  * Additional variables are generated based on new combinations or further processing of primary variables
  
* `indicators` : Indicator calculation
  * Indicators are calculated for each dataset. 
  * Individual indicators can be built by using their id code as a target e.g. `101`

* `ensstats` : Ensemble statistics
  * Indicators on a common grid can then be merged into a single object and ensemble statistics (e.g. median, mean 10th percentile, 90th percentile) calculated

* `arealstats` : Areal statistics
  * Indicator statistics are calculated for all polygons areas defined in `config.yaml`. 
 
* `plots` : Outputs
  * Produce ouput plots summarising all indicators

