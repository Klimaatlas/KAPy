# Bias adjustment script

import KAPy

# Prevent execution during Dask worker re-import
if "snakemake" in globals():
    client = KAPy.setup_dask_cluster(
        threads=snakemake.threads, resources=snakemake.resources
    )

    BA = KAPy.bias_adjustment(
        target_file=snakemake.input.target,
        reference_file=snakemake.input.ref,
        tempDir=snakemake.resources.tmpdir,
        **snakemake.params,
    )

    KAPy.write_variables(BA, dict(snakemake.output))
