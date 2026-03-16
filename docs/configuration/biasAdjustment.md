# KAPy bias adjustment configuration

*Bias adjustment is the process by which the outputs of a climate model are post-processed so that they match specific characteristics of the observed climate during a common period of time. In KAPy we wrap methods in two existing packages to enable bias adjustment - `python-cmethods` and `xclim`. The method employed is chosen via the `method` field, with the following valid options: 
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

- <a id="properties/id"></a>**`id`** *(string, required)*: Unique identifier for the bias adjustment task. Must match pattern: `^[^ ]+$` ([Test](https://regexr.com/?expression=%5E%5B%5E%20%5D%2B%24)). Items must be unique.
- <a id="properties/enabled"></a>**`enabled`** *(string or null, required)*: Determines whether the row be used in the workflow. A non-empty value indicates not to use that row.
- <a id="properties/outDatasetCode"></a>**`outDatasetCode`** *(string, required)*: DatasetCode that will be associated with bias-adjusted output. Note that the cominbation of variable name and DatasetCode must not be a duplicate of other combinations names found in the configuration of KAPy. This variable primarily serves to distinguish between raw and bias-adjusted variables e.g. `CORDEX` and `CORDEX-cal` The exact choice is not important, but it is recommended to adopt a consistent approach throughout the project.
- <a id="properties/baVariable"></a>**`baVariable`** *(string, required)*: The name of the variable to bias adjust, drawn from the list of primary and secondary variables. If the variable cannot be found, an error will be raised. KAPy assumes that the same variable name is used for both the model and observational data sources.
- <a id="properties/targetDataset"></a>**`targetDataset`** *(string, required)*: The dataset that will be bias adjusted e.g.  'CORDEX'. This is most commonly the output of a climate model, but need not be.
- <a id="properties/refDataset"></a>**`refDataset`** *(string, required)*: The dataset that will be used as the reference  data source to bias-adjust against, such as `ERA5`. Most commonly this will be an observational data set, a reanalysis or similar but it need not be. However, the combination of climate variable and dataset code should uniquely identify a single file within the variable palette of KAPy - if not, an error will be raised.
- <a id="properties/trainPeriodStart"></a>**`trainPeriodStart`** *(string, required)*: Start year of the training period. Data after and including 1 Jan of this year will be used for training the bias adjustment procedure. Must match pattern: `^\d{4}$` ([Test](https://regexr.com/?expression=%5E%5Cd%7B4%7D%24)).
- <a id="properties/trainPeriodEnd"></a>**`trainPeriodEnd`** *(string, required)*: End year of the training period. Data before and including 31 Dec of this year will be used for training the bias adjustment procedure. Must match pattern: `^\d{4}$` ([Test](https://regexr.com/?expression=%5E%5Cd%7B4%7D%24)).
- <a id="properties/method"></a>**`method`** *(string, required)*: Bias adjustment method to be used. See above for a clarification of options. Must be one of: "xclim-scaling", "xclim-eqm", or "xclim-dqm".
- <a id="properties/grouping"></a>**`grouping`** *(string)*: Apply bias-adjustment independently of each time grouping selected here. Must be one of: "none", "dayofyear", "month", or "season".
- <a id="properties/additionalArgs"></a>**`additionalArgs`** *(string, required)*: Additional arbitrary arguments specified as a dict to be passed to the function via keyword arguments. e.g. `{'kind'='+', group='time.month'}`. Can be an empty dict or empty string if no there are no additional parameters. e.g. `{}` .
- <a id="properties/customScriptPath"></a>**`customScriptPath`** *(string)*: If `method` is set to `custom`, this field is used to identify the path to a custom script, if applicable.
- <a id="properties/customScriptFunction"></a>**`customScriptFunction`** *(string)*: Name of the function in `customScriptPath` to be used for bias correction,  if applicable.
