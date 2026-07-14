import KAPy

# Prevent execution during Dask worker re-import
if "snakemake" in globals():
    client = KAPy.setup_dask_cluster(
        threads=snakemake.threads, resources=snakemake.resources
    )

    SV = KAPy.build_derived_variables(
        input_files=dict(snakemake.input), **snakemake.params
    )
    KAPy.write_variables(SV, dict(snakemake.output))
