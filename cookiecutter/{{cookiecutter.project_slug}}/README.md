# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

## About

This project uses the [KAPy](https://github.com/Klimaatlas/KAPy) framework to generate climate data and indicators.

KAPy is included in this project as a Git submodule:

```text
KAPy/
```

This keeps the project-specific configuration and workflow separate from the KAPy framework itself.

## Project structure

```text
.
├── KAPy/          # KAPy framework (Git submodule)
├── config/        # Project configuration
├── inputs/        # Input data
├── outputs/       # Generated output
├── Snakefile      # Main Snakemake workflow
└── README.md      # This file
```

### KAPy version

This project uses the KAPy repository as a Git submodule. The specific KAPy commit used by the project is recorded in the main project's Git repository.

To check the currently used KAPy commit:

```bash
git submodule status
```

To update the KAPy submodule to a newer commit on its configured branch:

```bash
git submodule update --remote KAPy
```

Review and commit the resulting submodule change in the main project repository.

## Running the workflow

Run the workflow using Snakemake according to the KAPy documentation and the configuration in:

```text
snakemake --cores 1 
```

## Configuration

Project-specific configuration is stored in:

```text
config/
```

Input data should be placed in:

```text
inputs/
```

and generated data and results are written to:

```text
outputs/
```

## KAPy

For information about the KAPy framework, its workflow, configuration options, and development, see the [KAPy repository](https://github.com/Klimaatlas/KAPy).


