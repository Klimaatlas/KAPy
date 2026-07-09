import yaml
import pandas as pd
import os
import ast
import jsonschema
from pathlib import Path


def readConfig(configfile):
    """
    Read config file

    Reads the KAPy config master file specified in the yaml format.
    """
    # Load file
    if os.path.exists(configfile):
        with open(configfile, "r") as f:
            cfg = yaml.safe_load(f)
    else:
        raise FileNotFoundError(
            f"Cannot find configuration file '{configfile}'. "
            + f"Working directory: '{os.getcwd()}'"
        )
    cfg["configfile"] = configfile
    return cfg


def validateConfig(config):
    """
    Inflate and validate config file

    Validates a loaded configuration (i.e. read directly from the KAPy config master
    file), inflates it by loading the configuration tables, and validates all elements
    against the appropriate validation schema. Returns the inflated validated config.
    """
    # Setup location of validation schemas
    schemaDir = Path(__file__).resolve().parent.parent / "schemas"

    # Do custom validation handling rather the using Snakemake's. The goal
    # here is to give a more user friendly error, when we fail. Thanks to ChatGPT
    # for the tip
    with open(os.path.join(schemaDir, "config.schema.json")) as f:
        cfgSchema = yaml.safe_load(f)
    try:
        jsonschema.validate(instance=config, schema=cfgSchema)
    except jsonschema.ValidationError as e:
        raise jsonschema.ValidationError(
            f'❌ Validation of "{config["configfile"]}" failed at "{".".join(map(str, e.path))}": {e.message}'
        )

    # Validate each configuration table in turn. The validation approach used
    # is defined in the following table
    tabularCfg = {
        "inputs": {
            "listCols": ["ensidFields"],
            "boolCols": ["mergeFiles"],
            "dictCols": [],
            "schema": "inputs",
            "optional": False,
        },
        "periods": {
            "listCols": [],
            "boolCols": [],
            "dictCols": [],
            "schema": "periods",
            "optional": False,
        },
        "seasons": {
            "listCols": ["months"],
            "boolCols": [],
            "dictCols": [],
            "schema": "seasons",
            "optional": False,
        },
        "secondaryVars": {
            "listCols": ["datasets", "inputVars", "outputVars"],
            "boolCols": ["passXarrays"],
            "dictCols": ["additionalArgs"],
            "schema": "derivedVars",
            "optional": True,
        },
        "biasAdjustment": {
            "listCols": [],
            "boolCols": [],
            "dictCols": ["additionalArgs"],
            "schema": "biasAdjustment",
            "optional": True,
        },
        "tertiaryVars": {
            "listCols": ["datasets", "inputVars", "outputVars"],
            "boolCols": ["passXarrays"],
            "dictCols": ["additionalArgs"],
            "schema": "derivedVars",
            "optional": True,
        },
        "indicators": {
            "listCols": ["indicator_codes", "variables", "seasons", "datasets"],
            "boolCols": ["skipna"],
            "dictCols": ["additionalArgs"],
            "schema": "indicators",
            "optional": True,
        },
        "dask_resources": {
            "listCols": [],
            "boolCols": [],
            "dictCols": [],
            "schema": "dask",
            "optional": True,
        },
    }
    for thisTblKey, theseVals in tabularCfg.items():
        # Load the tablular configuration table (if it  exists)
        if thisTblKey == "dask_resources":
            thisCfgFile = config[thisTblKey]
        else:
            thisCfgFile = config["configurationTables"][thisTblKey]

        if ((thisCfgFile == "") | (thisCfgFile is None)) & theseVals["optional"]:
            continue  # Not using this option
        elif (thisCfgFile == "") & theseVals["optional"]:
            raise ValueError(f"'{thisTblKey}' configuration table must be specified.")
        elif not os.path.exists(thisCfgFile):
            raise FileNotFoundError(
                f"Cannot find '{thisTblKey}' configuration table at path '{thisCfgFile}'."
            )
        thisTbl = pd.read_csv(
            thisCfgFile, sep="\t", comment="#", dtype="str", keep_default_na=False
        )
        # Drop rows that are disabled
        if "enabled" not in thisTbl:
            raise ValueError(
                f"Cannot find column 'enabled' in {thisTblKey} configuration table."
            )
        else:
            enabledRows = thisTbl["enabled"] != ""
            thisTbl = thisTbl[enabledRows]
        # Require a non-zero length
        if len(thisTbl) == 0:
            raise ValueError(
                f"'{thisTblKey}' configuration table at {thisCfgFile} is empty or all rows are disabled."
            )
        # Load the schema to validate against
        with open(os.path.join(schemaDir, f"{theseVals['schema']}.schema.json")) as f:
            thisSchema = yaml.safe_load(f)
        # Then validate row-by-row
        for i, row in enumerate(thisTbl.to_dict(orient="records")):
            try:
                jsonschema.validate(instance=row, schema=thisSchema)
            except jsonschema.ValidationError as e:
                raise jsonschema.ValidationError(
                    f'❌ Validation of "{thisCfgFile}" failed at row {i+1}, column "{".".join(map(str, e.path))}": {e.message}'
                )

        # Modifications----------------
        # If indicator_code column is empty, use the id instead
        if thisTblKey == "indicators":
            thisTbl["indicator_codes"] = [
                rw["id"] if rw["indicator_codes"] == "" else rw["indicator_codes"]
                for idx, rw in thisTbl.iterrows()
            ]

        # We allow some columns to be defined as lists, but
        # note that Snakemake doesn't validate arrays in tabular configurations at the moment
        # https://github.com/snakemake/snakemake/issues/2601
        # We therefore parse the list after validation (and validate this item as a string)
        for col in theseVals["listCols"]:
            thisTbl[col] = thisTbl[col].apply(
                lambda x: (
                    [item.strip() for item in x.split(",")] if pd.notnull(x) else []
                )
            )

        # Dict columns also need to be parsed
        for col in theseVals["dictCols"]:
            try:
                thisTbl[col] = [ast.literal_eval(x) for x in thisTbl[col]]
            except (SyntaxError, ValueError) as e:
                raise ValueError(
                    f"Error occurred in parsing column '{col}' in '{thisCfgFile}' : {e}"
                )

        # Convert boolean columns to a boolean type
        for col in theseVals["boolCols"]:
            thisTbl[col] = [str(s).strip().lower() == "true" for s in thisTbl[col]]

        # id Column needs to be unique
        duplicated_ids = thisTbl.loc[thisTbl["id"].duplicated(), "id"].unique()
        if len(duplicated_ids) > 0:
            raise ValueError(
                f"Duplicate ids values found in '{thisTblKey}' table: {list(duplicated_ids)}"
            )

        # Force id column to be a string. Set to as the index so it can be used as the key
        thisTbl["id"] = [str(x) for x in thisTbl["id"]]
        thisTbl = thisTbl.set_index("id", drop=False)

        # Put back into the config
        config[thisTblKey] = thisTbl.to_dict(orient="index")

    # Manual validation -----------------
    # Some things are a bit tricky to validate with JSON schemas alone, particular where
    # we have validations that cross schemes. The following checks are therefore done
    # manually.
    # Firstly, We need to validate the months part of the seasons table manually.
    for thisKey, theseValues in config["seasons"].items():
        theseMnths = theseValues["months"]
        if len(theseMnths) > 12:
            raise ValueError("Between 1 and 12 months should be selected")
        if len(theseMnths) == 0:  # Set to all months
            theseMnths = list(range(1, 13))
        # Length is ok. Now convert to integers
        theseMnths = [int(i) for i in theseMnths]
        if max(theseMnths) > 12 | min(theseMnths) < 1:
            raise ValueError("Month specification must be between 1 and 12 inclusive")
        # Write the integers back to finish
        config["seasons"][thisKey]["months"] = theseMnths

    # Require that units are consistent across a variable
    inputvarDf = pd.DataFrame.from_dict(config["inputs"], orient="index")
    unitCount = inputvarDf.groupby("varCode")["units"].nunique()
    if any(unitCount > 1):
        multiUnits = unitCount[unitCount > 1].index
        raise ValueError(
            f"Variable '{multiUnits[0]}' has {unitCount[multiUnits[0]]} different units defined. Please ensure consistency between units in the same varCode."
        )

    # Season selected in the indicator table must be valid
    indTbl = pd.DataFrame.from_dict(config["indicators"], orient="index")
    validSeasons = list(config["seasons"].keys()) + ["all"]
    for idx, thisrw in indTbl.iterrows():
        for requestSeason in thisrw["seasons"]:
            if requestSeason not in validSeasons:
                raise ValueError(
                    f"Unknown season '{requestSeason}' requested for indicator '{thisrw['id']}'."
                )

    # Indicators can only take multiple input variables if the statistic type is "custom"
    for idx, rw in indTbl.iterrows():
        if (rw["statistic"] != "custom") & (len(rw["variables"]) > 1):
            raise ValueError(
                f"Multiple variables supplied to indicator '{rw['id']}': in this case, the statistic chosen needs to be 'custom' but is currently '{rw['statistic']}'."
            )

    # Check if the configuration file is valid
    if config["arealstats"]["shapefile"] is not None:
        if not os.path.exists(config["arealstats"]["shapefile"]):
            raise FileNotFoundError(
                f"Cannot find shapefile declared in config/arealstats/shapefile: '{config['arealstats']['shapefile']}'."
            )

    return config


def getConfig(configfile):
    """
    Load and validate config file

    Reads the KAPy config master file specified in the yaml format using readConfig()
    and then validates it using validateConfig()
    """
    cfg = readConfig(configfile)
    cfg = validateConfig(cfg)
    return cfg


# Validation ----------------------------
if __name__ == "__main__":
    # Setup for debugging
    from pathlib import Path

    pd.set_option("display.max_colwidth", None)
    this_path = Path(__file__).resolve().parent.parent.parent
    os.chdir(this_path)

    # Validate base configuration
    config = readConfig("./config/config.yaml")
    cfg = validateConfig(config)

    # Testing configuration
    config = readConfig("./workflow/testing/config.yaml")
    cfg = validateConfig(config)
