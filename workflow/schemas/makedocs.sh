#!/bin/bash
set -e

# Loop over files in the directory
for file in ./*.json; do
    # Check if file is a regular file
    if [ -f "$file" ]; then
        echo "Processing file: $file"
        # Run the command on the file
	jsonschema2md "$file" ../../docs/configuration/$(echo "$file" | sed "s/\.schema\.json$/.md/")
        # Check the exit status of the command
        if [ $? -ne 0 ]; then
            echo "Error: Command failed for file $file"
            # Handle the error if needed

        fi
    fi
done

