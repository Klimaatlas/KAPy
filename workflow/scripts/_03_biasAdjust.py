import KAPy

BA=KAPy.biasAdjust(target_file=snakemake.input.target,
                    reference_file=snakemake.input.ref,
                    **snakemake.params)
KAPy.write_variables(BA,dict(snakemake.output))
