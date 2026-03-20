# KAPy periods configuration

*Calculation periods in KAPy are configured through a tab-separated table, with one row per period. At least one period must be defined, even in configurations where there is no `period` time-binning used, as the first period is used as the reference period against which changes in indicators are calculated. The available options are described here. All options are required.*

## Properties

- <a id="properties/id"></a>**`id`** *(string, required)*: Unique identifier for the period. This can be numeric, but will be treated as a string. Cannont contain space. Must match pattern: `^[^ ]+$` ([Test](https://regexr.com/?expression=%5E%5B%5E%20%5D%2B%24)). Items must be unique.
- <a id="properties/enabled"></a>**`enabled`** *(string or null, required)*: Determines whether the row be used in the workflow. A non-empty value indicates not to use that row.
- <a id="properties/description"></a>**`description`** *(string)*: Description/name of the period. Stored in the output database.
- <a id="properties/start"></a>**`start`** *(string, required)*: The start year of the period. The full year is included in the calculation. Must match pattern: `^\d{4}$` ([Test](https://regexr.com/?expression=%5E%5Cd%7B4%7D%24)).
- <a id="properties/end"></a>**`end`** *(string, required)*: The end year of the period. The full year is included in the calculation. Must match pattern: `^\d{4}$` ([Test](https://regexr.com/?expression=%5E%5Cd%7B4%7D%24)).
