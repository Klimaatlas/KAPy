import KAPy

# Prevent execution during Dask worker re-import
if "snakemake" in globals():
    client = KAPy.setupDaskCluster(
        threads=snakemake.threads, resources=snakemake.resources
    )

    rgd = KAPy.regrid(
        input_path=snakemake.input,
        tempDir=snakemake.resources.tmpdir,
        **snakemake.params,
    )
    KAPy.write_indicators(rgd, snakemake.output)
