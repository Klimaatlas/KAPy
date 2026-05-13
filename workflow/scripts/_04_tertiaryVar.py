import KAPy

TV=KAPy.buildDerivedVar(inFiles=dict(snakemake.input),
                        **snakemake.params)
KAPy.write_variables(TV,dict(snakemake.output))
