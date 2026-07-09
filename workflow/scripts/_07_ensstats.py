import KAPy

ens = KAPy.generateEnsstats(inFiles=snakemake.input, **snakemake.params)

# Write out
ens.to_netcdf(snakemake.output[0])
