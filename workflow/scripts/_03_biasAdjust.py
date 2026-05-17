# import KAPy

# #Configure dask 
# config=snakemake.config
# client=KAPy.setupDaskCluster(nWorkers=config['advanced']['nWorkers'],
#                      threadsPerWorker=config['advanced']['threadsPerWorker'],
#                      memoryPerWorker=config['advanced']['memoryPerWorker'])

# #Perform bias adjustment
# BA=KAPy.biasAdjust(target_file=snakemake.input.target,
#                     reference_file=snakemake.input.ref,
#                     **snakemake.params)
# KAPy.write_variables(BA,dict(snakemake.output))

import KAPy

def main():
    config = snakemake.config

    client = KAPy.setupDaskCluster(
        nWorkers=config['advanced']['nWorkers'],
        threadsPerWorker=config['advanced']['threadsPerWorker'],
        memoryPerWorker=config['advanced']['memoryPerWorker']
    )

    BA = KAPy.biasAdjust(
        target_file=snakemake.input.target,
        reference_file=snakemake.input.ref,
        tempDir= snakemake.resources.tmpdir,
        **snakemake.params
    )

    KAPy.write_variables(BA, dict(snakemake.output))


# IMPORTANT: prevent execution during Dask worker re-import
if "snakemake" in globals():
    main()