import KAPy

KAPy.generateEnsstats(outFile=snakemake.output,
                        inFiles=snakemake.input,
                        **snakemake.params)
