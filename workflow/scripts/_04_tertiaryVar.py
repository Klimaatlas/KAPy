import KAPy

# Prevent execution during Dask worker re-import
if "snakemake" in globals():
    client = KAPy.setupDaskCluster(
        threads=snakemake.threads, resources=snakemake.resources
    )

    TV = KAPy.buildDerivedVar(inFiles=dict(snakemake.input), **snakemake.params)
    KAPy.write_variables(TV, dict(snakemake.output))
