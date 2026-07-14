import KAPy

# Prevent execution during Dask worker re-import
if "snakemake" in globals():
    client = KAPy.setup_dask_cluster(
        threads=snakemake.threads, resources=snakemake.resources
    )

    inds = KAPy.calculate_indicators(
        input_files=dict(snakemake.input), **snakemake.params
    )
    KAPy.write_indicators(inds, dict(snakemake.output))
