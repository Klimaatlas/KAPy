import KAPy

dfOut = KAPy.generate_areal_statistics(
    inFile=snakemake.input.inputFile[0],
    tempDir=snakemake.resources.tmpdir,
    **snakemake.params,
)

# Write results out
dfOut.to_csv(snakemake.output[0], index=False)
