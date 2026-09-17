# KAPy - *Klimaatlases* in Python

KAPy (Klimaatlas in Python) is a pipeline for processing data to support climate services using reproducible, automated workflows.
KAPy aims to be open-source, transparent, repeatible and flexible, and works from ensembles of climate models such as CMIP and CORDEX together with observations. KAPy has its roots in the pipeline originally developed to power the Danish Meteorological Institute's *Klimaatlas* climate service, but is  a ground-up python-based rethink that is intended to be used widely.     

## Getting started

Here we provide a concise set of sets describe the basic steps to install and configure KAPy. For a more detailed version see the [installation guide](./docs/installation.md).

KAPy uses [Conda](https://conda.io/projects/conda/en/latest/index.html) to manage its software environment. If you do not already have Conda installed, please install it first.

Create the KAPy environment:

```bash
conda env create -f https://raw.githubusercontent.com/Klimaatlas/KAPy/refs/heads/main/workflow/envs/env.yaml
```

Activate the environment:

```bash
conda activate KAPy
```

Create a new KAPy project using the project template:

```bash
cookiecutter --directory cookiecutter gh:Klimaatlas/KAPy
```

Follow the prompts to configure your project. Cookiecutter will create a new project directory containing the required KAPy files and configuration.

Move into the new project directory and run the workflow:

```bash
snakemake --cores 1
```

**Ka pai  — you are ready to use KAPy!**


## Documentation

Documentation for KAPy is contained in the `./docs` folder. For more details, please see the following [Documentation Overview](./docs/README.md).

## Contributing

KAPy is in active development and welcomes all contributions, both large and small.  
    
* If you have a suggestion for a new feature or want to report a bug, please file an issue via the issue tracker.
* If you would like to contribute code or documentation, check out the [Contributing Guidelines](./docs/CONTRIBUTING.md) before you begin!

## How to cite KAPy

If you wish to cite KAPy in your work, please cite this repository (https://github.com/Klimaatlas/KAPy/) and the release version. A publication describing KAPy will be prepared in the future.

## License

KAPy is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License. A copy of this license is available in the root director ([LICENSE](./LICENSE)).
    
## Code of Conduct

A code of conduct for the KAPy community is found in the [Code of Conduct](./docs/Code_of_conduct.md). In short: be kind.
    
## Credits
    
The development of KAPy is financed via a grant from the Danish Central Government to the Danish Meteorological Institute.    
    
## Why KAPy?

KAPy takes its name from joining the `KA` from DMI's *Klimaatlas* with the `Py` from Python, in the style of many Python libraries. 

More importantly, the name is also a homonym for the phrase *ka pai* from *Te Reo Māori*, the language of the Māori people, the *tangata whenua* (indigenous people) of Aotearoa New Zealand. The phrase means simply "good", but can also be used as praise, as in "well done". e.g.
```
Son: Look Dad! I made a Klimaatlas in Python!
Dad: Ka pai, son, ka pai!
```
