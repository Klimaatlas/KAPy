import KAPy

rgd=KAPy.regrid(input_path=snakemake.input,
                tempDir= snakemake.resources.tmpdir,
            **snakemake.params)
KAPy.write_indicators(rgd,
                      snakemake.output)
