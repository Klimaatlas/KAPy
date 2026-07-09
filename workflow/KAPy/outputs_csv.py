import pandas as pd
import os
from pathlib import Path


def mergeCSVs(outFile, inFiles):
    # Load data file function
    def prepareDataFile(thisPath):
        # Load file
        datIn = pd.read_csv(thisPath, dtype=str, keep_default_na=False)

        # Process filename
        datIn.insert(0, "filename", os.path.basename(thisPath))
        datIn.insert(
            2,
            "memberID",
            datIn["filename"].str.extract("^[^_]+_[^_]+_[^_]+_[^_]+_(.*).csv$"),
        )
        datIn.insert(
            2, "expt", datIn["filename"].str.extract("^[^_]+_[^_]+_[^_]+_([^_]+)_.*$")
        )
        datIn.insert(
            2, "gridID", datIn["filename"].str.extract("^[^_]+_[^_]+_([^_]+)_.*$")
        )
        datIn.insert(2, "datasetID", datIn["filename"].str.extract("^([^_]+)_.*$"))
        datIn.insert(2, "indID", datIn["filename"].str.extract("^[^_]+_([^_]+)_.*$"))

        # Set the name of the time dimension to be periodID.

        # Finish
        datOut = datIn.drop(columns=["filename"])
        return datOut

    # Delete the output file if it exists
    if os.path.exists(outFile):
        os.remove(outFile)

    # Load and then write data individually to a merged file
    # Only write the header if the file doesn't exist
    firstFile = True
    for f in inFiles:
        df = prepareDataFile(f)
        if firstFile:
            column_order = (
                df.columns
            )  # Fix column order to match the first file. Avoid problems with switching
        df.to_csv(
            outFile, index=False, columns=column_order, mode="a", header=firstFile
        )
        firstFile = False


# Development setup -----------------------------------------------------
if __name__ == "__main__":
    # Set the working directory
    from pathlib import Path

    ROOT = Path(__file__).resolve().parent.parent.parent

    # Import KAPy
    os.chdir(ROOT / "workflow")
    import KAPy

    os.chdir(ROOT)

    # Get configuration file and therefore filelist
    config = KAPy.getConfig("./config/config.yaml")
    wf = KAPy.getWorkflow(config)
    inFiles = wf["mergedCSVs"]["members"]

    # And the output file
    OUTPUT_PATHS = KAPy.get_OUTPUT_PATHS(config["outputDir"])
    outFile = OUTPUT_PATHS["ensembleMembersCSV"]

    # Run the function
    mergeCSVs(outFile, inFiles)
