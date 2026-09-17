# KAPy - *Klimaatlases* in Python

KAPy (Klimaatlas in Python) is a pipeline for processing data to support climate services using reproducible, automated workflows.
KAPy aims to be open-source, transparent, repeatible and flexible, and works from ensembles of climate models such as CMIP and CORDEX together with observations. KAPy has its roots in the pipeline originally developed to power the Danish Meteorological Institute's *Klimaatlas* climate service, but is  a ground-up python-based rethink that is intended to be used widely.     

## Getting started

Here we describe the basic steps to install and configure KAPy. First, you need to setup the Python environment containing the packages used by KAPy: this environment also includes tools that can quickly configure KAPy. KAPy leans heavily on the Conda package manager: if you don't have it installed already, it can be downloaded from  https://conda.io/projects/conda/en/latest/index.html. Conda can work directly from the GitHub repository - on an internet connected machine, run the following command to create the 'KAPy' environment:

```
conda env create -f https://raw.githubusercontent.com/Klimaatlas/KAPy/refs/heads/main/workflow/envs/env.yaml
```

You should now have a working conda environment called 'KAPy'. To activate the environment, run:

```
conda activate KAPy
```

The KAPy environment contains a cookiecutter template, which can be used to quickly set up a new project. To use the template, run:

```
cookiecutter --directory cookiecutter gh:Klimaatlas/KAPy
```

Follow the instructions and explanations on screen: cookiecutter  will create a new folder containing a template KAPy project in the current working directory, based on the user's configuration. The project can be run from within the new folder using the commmand:

```
snakemake --cores 1
```

And so you're ready to go. To get familiar with the workings of KAPy, or for a more detailed description of the installation process, we recommend looking at the documentation in the `./docs` folder, and particularly the [Tutorials](./docs/tutorials/README.md).  


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
