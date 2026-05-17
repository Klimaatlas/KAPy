import KAPy

KAPy.generateArealstats(outFile=snakemake.output,
                        inFile=snakemake.input.inputFile,
                        tempDir= snakemake.resources.tmpdir,
                        **snakemake.params)
