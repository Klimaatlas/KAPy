import KAPy

# Prevent execution during Dask worker re-import
if "snakemake" in globals():
    client = KAPy.setupDaskCluster(threads=snakemake.threads,
                                   resources=snakemake.resources)

    inds=KAPy.calculateIndicators(inFiles=dict(snakemake.input),
                                **snakemake.params)
    KAPy.write_indicators(inds,dict(snakemake.output))

