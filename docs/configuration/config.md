# JSON Schema

*Configuration schema for KAPy configuration objects. These configurations are usually stored in the `config.yaml` file in the root directory of the project.*

## Properties

- **`domain`** *(object)*: Test.
  - **`xmin`** *(number, required)*
  - **`xmax`** *(number, required)*
  - **`dx`** *(number, required)*
  - **`ymin`** *(number, required)*
  - **`ymax`** *(number, required)*
  - **`dy`** *(number, required)*
- **`inputs`** *(string)*
- **`indicators`** *(string)*
- **`scenarios`** *(string)*
- **`notebooks`** *(string)*
- **`periods`** *(string)*
- **`seasons`** *(string)*
- **`arealstats`** *(object)*
  - **`calcForMembers`** *(boolean, required)*
- **`dirs`** *(object)*
  - **`primVars`** *(string, required)*
  - **`bc`** *(string, required)*
  - **`indicators`** *(string, required)*
  - **`regridded`** *(string, required)*
  - **`ensstats`** *(string, required)*
  - **`arealstats`** *(string, required)*
  - **`notebooks`** *(string, required)*
- **`ensembles`** *(object)*
  - **`upperPercentile`** *(integer, required)*
  - **`centralPercentile`** *(integer, required)*
  - **`lowerPercentile`** *(integer, required)*
- **`primVars`** *(object)*
  - **`storeAsNetCDF`** *(boolean, required)*
- **`regridding`** *(object)*
  - **`method`** *(string, required)*
