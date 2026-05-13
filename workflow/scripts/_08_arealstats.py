import KAPy

KAPy.generateArealstats(outFile=snakemake.output,
                        inFile=snakemake.input.inputFile,
                        **snakemake.params)
