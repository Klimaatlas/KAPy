# Primary variables

import KAPy

# Prevent execution during Dask worker re-import
if "snakemake" in globals():
    client = KAPy.setupDaskCluster(
        threads=snakemake.threads, resources=snakemake.resources
    )

    da = KAPy.buildPrimVar(
        inFiles=list(snakemake.input),
        cutoutArgs=snakemake.params.cutout_args,
        **snakemake.params.row_arguments,
    )
    KAPy.write_variables(
        da, {snakemake.params.row_arguments["varCode"]: snakemake.output[0]}
    )
