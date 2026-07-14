# Primary variables

import KAPy

# Prevent execution during Dask worker re-import
if "snakemake" in globals():
    client = KAPy.setup_dask_cluster(
        threads=snakemake.threads, resources=snakemake.resources
    )

    da = KAPy.build_primary_variable(
        input_files=list(snakemake.input),
        cutout_arguments=snakemake.params.cutout_args,
        **snakemake.params.row_arguments,
    )
    KAPy.write_variables(
        da, {snakemake.params.row_arguments["variable_code"]: snakemake.output[0]}
    )
