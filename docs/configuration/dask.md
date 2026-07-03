# Dask Resource Configuration

*Configuration of resources to be used by Dask in each rule is achieved a tab-separated table, with one row per Snakemake rule. Resources for generic families of rules (e.g. BIAS_ADJUSTMENT) can be specified together, and are inherited across all BIAS_ADJUSTMENT rules. Resources for individual rules can also be specified and override the family-level rules - rule specification is based on the id in the corresponding configuration table. Currently only LocalClusters are supported, while disabling the row uses the default scheduler. Arguments to LocalCluster() can be specified via the columns, with additional arguments to the LocalCluster also being possible. For more details, see the documentation of `LocalCluster()`: https://docs.dask.org/en/stable/deploying-python.html#reference*

## Items

- <a id="items"></a>**Items** *(object)*: Cannot contain additional properties.
  - <a id="items/properties/id"></a>**`id`** *(string, required)*: Identifier for the pipeline stage or configuration block (e.g. PRIMARY_VARIABLES, BIAS_ADJUSTMENT). Length must be at least 1.
  - <a id="items/properties/enabled"></a>**`enabled`** *(string or null, required)*: Determines whether to use the Dask LocalCluster for the corresponding row.
  - <a id="items/properties/n_workers"></a>**`n_workers`** *(integer, required)*: Number of worker processes to start in the cluster. Minimum: `1`.
  - <a id="items/properties/threads_per_worker"></a>**`threads_per_worker`** *(integer, required)*: Number of threads allocated per worker process. Minimum: `1`.
  - <a id="items/properties/memory_limit"></a>**`memory_limit`** *(string, required)*: Memory limit assigned to each worker (e.g. 1000MB, 4GB).
