import KAPy

rgd=KAPy.regrid(input_path=snakemake.input,
            **snakemake.params)
KAPy.write_indicators(rgd,
                      snakemake.output)
