import KAPy

# Prevent execution during Dask worker re-import
if "snakemake" in globals():
    client = KAPy.setupDaskCluster(
        threads=snakemake.threads, resources=snakemake.resources
    )

    SV = KAPy.buildDerivedVar(inFiles=dict(snakemake.input), **snakemake.params)
    KAPy.write_variables(SV, dict(snakemake.output))
