"""
Constants for internal output layout used by KAPy.

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

# Mapping of logical output names to their relative subdirectories/filenames.
# These are joined with the configured base output directory at runtime.
PATHS = {
    "primaryVariables": "01.primaryVars",
    "secondaryVariables": "02.secondaryVars",
    "biasAdjustment": "03.biasAdjustment",
    "tertiaryVariables": "04.tertiaryVars",
    "indicators": "05.indicators",
    "regridded": "06.commmon_grid",
    "ensstats": "07.ensstats",
    "arealstats": "08.areal_statistics",
    "ensembleStatisticsCSV": "Ensemble_statistics.csv",
    "ensembleMembersCSV": "Ensemble_members.csv",
    "database": "KAPy_outputs.sqlite",
}
