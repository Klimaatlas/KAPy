import subprocess
from pathlib import Path
import shutil
import tempfile
import urllib.request
import zipfile

project_dir = Path.cwd()

# Initialize the new project as a Git repository
subprocess.run(
    ["git", "init","-b","main"],
    cwd=project_dir,
    check=True,
)

# Select the KAPy branch
kapy_branch = "dev"

# Add KAPy as a submodule
subprocess.run(
    [
        "git", "submodule", "add",
        "-b", kapy_branch,
        "https://github.com/Klimaatlas/KAPy.git",
        "KAPy",
    ],
    cwd=project_dir,
    check=True,
)

# Copy the appropriate configuration
if "{{ cookiecutter.configuration_type }}"=="full":
    config_source = project_dir / "KAPy/workflow/testing"
else:
    config_source = project_dir / "KAPy/config"

shutil.copytree(
    config_source,
    project_dir / "config",
    dirs_exist_ok=True,
)

# Move additional files into the correct locations for the full configuration
if "{{ cookiecutter.configuration_type }}"=="full":
    Path.mkdir(project_dir / "resources/shapefiles", parents=True, exist_ok=True)
    shutil.copytree(    
        project_dir / "KAPy/docs/tutorials/resources/shapefiles",
        project_dir / "resources/shapefiles",
        dirs_exist_ok=True
    )   
    shutil.move(    
        project_dir / "config/griddes.txt",
        project_dir / "resources/",
    )   

# Download sample dataset
dataset_url = "https://download.dmi.dk/Research_Projects/KAPy/tas_example_dataset.zip"

if {{ cookiecutter.download_sample_dataset }}:
    inputs_dir = project_dir / "inputs"

    print("Downloading sample dataset...")

    with tempfile.TemporaryDirectory() as tmpdir:
        archive = Path(tmpdir) / "sample_data.zip"

        urllib.request.urlretrieve(
            dataset_url,
            archive,
        )

        print("Extracting sample dataset...")

        with zipfile.ZipFile(archive, "r") as zip_file:
            zip_file.extractall(inputs_dir)

    print("Sample dataset installed in inputs/")

# Create initial commit
subprocess.run(
    ["git", "add", "."],
    cwd=project_dir,
    check=True,
)

subprocess.run(
    ["git", "commit", "-m", "Initial project setup"],
    cwd=project_dir,
    check=True,
)

print(" \n")
print("=" * 70)
print("Setup completed succesfully. Ka pai!")
print("=" * 70)

