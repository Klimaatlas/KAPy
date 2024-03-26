# KAPy input configuration

*The configuration of inputs in KAPy is set through a tab-separated table, with one row per input variable. The available configuration options are described here. All options are required*

## Properties

- **`id`** *(string)*: Identifier for the input. Must be unique. It is usually easiest to join the srcName and varName together into one string.
- **`srcName`** *(string)*: The name of the data source e.g CORDEX, ERA5. Need not be unique. Is used to group related variables from the same datasource together further in the analysis (e.g. tas and pr from ERA5). .
- **`varName`** *(string)*: The name of the variable contained in this dataset. While there is no enforcement of naming conventions in KAPy, the variable names should anyway be standardised across the entire configuration and across input datasets. For example, both ERA5 and CORDEX provide surface temperature, but with different internal variable names in the input files - to ensure that they can be matched together, they should both be assigned the varName `tas`.
- **`path`** *(string)*: Path to input files, relative to the working directory. Glob-matching (e.g. `./resources/CORDEX/tas_*`) can be used when then input covers multiple files  and/or there are multiple variable types in the same directory.
- **`regex`** *(string)*: A regular expression used to group files together. Climate models outputs are often split into timeslices that need to be joined back together before use. This regular expression can be used to identify the parts of a filename (the 'stem' in KAPy language) that act as unique identifiers for the data source, and can therefore be used as a basis for grouping. Stems are identified as matching group, in brackets. e.g. `^tas_(.*)_.*?.nc$`.
- **`internalVarName`** *(string)*: The internal variable name stored within the input file that corresponds to varName. For example, in ERA5 files the internal variable name for surface temperature is `t2m`.
- **`hasScenarios`** *(boolean)*: Indicates whether the input source has emissions scenarios associated with it. If so, the [scenario configuration table](scenarios.md) will used to further group input files together for this input source.
- **`applyPreprocessor`** *(boolean)*: Allows application of a preprocessing script to tidy inputs before they are written to disk as primVars. Different preprocessors can be used for different applications.
- **`preprocessorPath`** *(['null', 'string'])*: Path to the script containing the preprocessor.
- **`preprocessorFunction`** *(['null', 'string'])*: Name of the preprocessor function to apply.
