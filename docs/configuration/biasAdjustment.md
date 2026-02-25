# KAPy bias adjustment configuration

*bias adjustment is the process by which the outputs of a climate model are post-processed so that they match specific characteristics of the observed climate during a common period of time. In KAPy we wrap methods in two existing packages to enable model bias adjustment - `python-cmethods` and `xclim`. The method employed is chosen via the `method` field, with the following valid options: 
 * `xclim-scaling` - [Scaling bias-adjustment](https://xclim.readthedocs.io/en/stable/api.html#adjustment-methods) from the `xclim`package.
 * `xclim-eqm` - [Empirical Quantile Mapping](https://xclim.readthedocs.io/en/stable/api.html#adjustment-methods) from the `xclim`package. 
 * `xclim-dqm` - [Detrended Quantile Mapping](https://xclim.readthedocs.io/en/stable/api.html#adjustment-methods) from the `xclim`package. 
  
 In addition, we plan on implementing the following methods in a future release: 
 * `cmethods-linear` - [Linear Scaling](https://python-cmethods.readthedocs.io/en/latest/methods.html#linear-scaling). 
  * `cmethods-variance` - [Variance scaling](https://python-cmethods.readthedocs.io/en/latest/methods.html#variance-scaling) 
  *  `cmethods-delta`- [Delta method](https://python-cmethods.readthedocs.io/en/latest/methods.html#variance-scaling) 
  * `cmethods-quantile` - [Quantile Mapping](https://python-cmethods.readthedocs.io/en/latest/methods.html#quantile-mapping) 
 * `cmethods-detrended` - [Detrended Quantile Mapping](https://python-cmethods.readthedocs.io/en/latest/methods.html#detrended-quantile-mapping) 
 * `cmethods-quantile-delta` - [Quantile Delta Mapping](https://python-cmethods.readthedocs.io/en/latest/methods.html#quantile-delta-mapping) 
 * `custom` - Use a custom script, as specified in the `customScriptPath` and `customScriptFunction` arguments. 
  
  For more information, see the documentation on the relevant packages: 
 * `python-cmethods` - https://python-cmethods.readthedocs.io/en/latest/index.html 
  * `xclim` https://xclim.readthedocs.io/en/stable/sdba.html*

## Properties

- **`id`** *(string, required)*: Unique identifier for the bias adjustment procedure. Must match pattern: `^[^ ]+$` ([Test](https://regexr.com/?expression=%5E%5B%5E%20%5D%2B%24)). Items must be unique.
- **`outDatasetID`** *(string, required)*: DatasetID that will be associated with bias-adjusted output. Note that the cominbation of variable name and DatasetID  must not be a duplicate of other combinations names found in the configuration of KAPy. This variable primarily serves to distinguish between raw and bias adjusted variables e.g.  `CORDEX` and `CORDEX-cal` The exact choice is not important, but it is recommended to adopt a consistent approach throughout the project.
- **`biasAdjustVariable`** *(string, required)*: The name of the variable to apply bias adjustment to, drawn from the list of primary and secondary variables. If the variable cannot be found, an error will be raised. KAPy assumes that the same variable name is used for both the model and observational data sources.
- **`targetDatasetID`** *(string, required)*: The ID of the dataset on which bias adjustment will be performed e.g. `CORDEX`. This is most commonly the output of a climate model, but need not be.
- **`refDatasetID`** *(string, required)*: The ID of the dataset that will be used as the reference data source to perform bias adjustment against, such as `ERA5`. Most commonly this will be an observational data set, a reanalysis or similar but it need not be. However, the combination of climate variable and datasetID should uniquely identify a single file within the variable palette of KAPy - if not, an error will be raised.
- **`calPeriodStart`** *(string, required)*: Start year of the bias adjustment period. Data after and including 1 Jan of this year will be used for bias adjustment. Must match pattern: `^\d{4}$` ([Test](https://regexr.com/?expression=%5E%5Cd%7B4%7D%24)).
- **`calPeriodEnd`** *(string, required)*: End year of the bias adjustment period. Data before and including 31 Dec of this year will be used for bias adjustment. Must match pattern: `^\d{4}$` ([Test](https://regexr.com/?expression=%5E%5Cd%7B4%7D%24)).
- **`method`** *(string, required)*: bias adjustment method to be used. See above for a clarification of options. Must be one of: `["xclim-scaling", "xclim-eqm", "xclim-dqm"]`.
- **`grouping`** *(string)*: Apply bias adjustment independently of each time grouping selected here. Must be one of: `["none", "dayofyear", "month", "season"]`.
- **`additionalArgs`** *(string, required)*: Additional arbitrary arguments specified as a dict to be passed to the function via keyword arguments. e.g. `{'kind'='+', group='time.month'}`. Can be an empty dict or empty string if no there are no additional parameters. e.g. `{}` .
- **`customScriptPath`** *(string)*: If `method` is set to `custom`, this field is used to identify the path to a custom script, if applicable.
- **`customScriptFunction`** *(string)*: Name of the function in `customScriptPath` to be used for bias correction,  if applicable.
