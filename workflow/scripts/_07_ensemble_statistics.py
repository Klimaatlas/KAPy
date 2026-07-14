import KAPy

ens = KAPy.calculate_ensemble_statistics(
    input_files=snakemake.input, **snakemake.params
)

# Write out
ens.to_netcdf(snakemake.output[0])
