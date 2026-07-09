import KAPy

dfOut = KAPy.generateArealstats(
    inFile=snakemake.input.inputFile[0],
    tempDir=snakemake.resources.tmpdir,
    **snakemake.params,
)

# Write results out
dfOut.to_csv(snakemake.output[0], index=False)
