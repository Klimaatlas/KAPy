import KAPy

SV=KAPy.buildDerivedVar(inFiles=dict(snakemake.input),
                        **snakemake.params)
KAPy.write_variables(SV,dict(snakemake.output))
