import KAPy

inds=KAPy.calculateIndicators(inFiles=dict(snakemake.input),
                            **snakemake.params)
KAPy.write_indicators(inds,dict(snakemake.output))

