"""
Constants for internal used by KAPy.
"""

"""
The `PATHS` mapping defines the *relative* subdirectories and filenames
used for KAPy outputs. These are joined with a configurable base output
directory elsewhere in the code, e.g.:

    output_root / PATHS["primaryVariables"]

The primary mode of use is via the KAPy.helpers.get_OUTPUT_PATHS() function,
which uses this constant mapping together with the outputDir configuration 
argument to construct the full path to each output file.

The keys are logical names used throughout the workflow; the values are
relative paths (directories or filenames) and should be treated as
internal, stable implementation details rather than user-configurable
settings.
"""
PATHS = {
    "primary_variables": "01.primary_variables",
    "secondary_variables": "02.secondary_variables",
    "bias_adjustment": "03.bias_adjustment",
    "tertiary_variables": "04.tertiaryVars",
    "indicators": "05.indicators",
    "regrid": "06.regrid",
    "ensemble_statistics": "07.ensemble_statistics",
    "areal_statistics": "08.areal_statistics",
    "ensemble_statistics_csv": "Ensemble_statistics.csv",
    "ensemble_members_csv": "Ensemble_members.csv",
    "database": "KAPy_outputs.sqlite",
}


"""
Chunking - an adventure in time and space

These constants control the dask-chunking used throughout KAPy. They are primarily used in the creation
of output files to ensure somewhat efficient read patterns that also work well with time-series dependent
operations such as bias adjustment. The spatial chunking is determined by the need to limit chunk-size to around 10-100MB when data is being
read for bias-adjustment (with all data in one contiguous block). The temporal chunking is more oriented towards seasonal subsetting when
calculating indicators - we want to avoid having to read the entire data block every time. The combination of the two also reflects a tradeoff to avoid excessive 
reading overhead.
"""
CHUNKING_TIME = 256
CHUNKING_SPACE = 16
