# KAPy - *Klimaatlases* in Python

KAPy is to create an open-source and flexible framework that can be used to generate climate indicators anywhere in the world, working from both CMIP and CORDEX datasets. KAPy is a ground-up python-based rethink of the pipeline originally developed to power the Danish Meterological Institute's *Klimaatlas* climate service.

## Getting started

Here we describe the basic steps to install and configure KAPy. Start by cloning the latest version of the code from the repository:

```
git clone git@github.com:Klimaatlas/KAPy.git
```

Next, we need to setup the Python environment, containing the packages used by KAPy. The list of packages can be found in the file `./configs/eny.yaml`. Depending on your favoured python package manager, the exact way that you use this list to create an environment may vary - this example is using Conda:

```
conda create --file /configs/eny.yaml
```

The resulting environment (called `KAPy`) can then be activated and used:

```
conda activate KAPy
```

Finally, a configuration file, `config.yaml`, needs to be availably in the project base directory. Configuration files are stored in the folder `./configs` under version control and are best soft-linked into place - this allows for a rapid reconfiguration of the engine. e.g.

```
ln -sf configs/Ghana/config.yaml 
```

Note that `config.yaml` files in the project directory are ignored by git, to avoid potential conflicts between users with different configurations.

## Usage

A list of targets available to build in the snakefile can be obtained with
```
    snakemake -l
```

An individual target can be built like so
```
    snakemake downloads --cores 1 -k
``` 
where the `--cores 1` argument will build the target with a single processor, and `-k` indicates that snakemake should "keep-going" if it encounters problems. Individual files can also be specified as targets. A full list of command like arguments to snakemake can be found in the documentation, https://snakemake.readthedocs.io/en/stable/executing/cli.html

## Workflow

KAPy is structured around a central package of tools, collated together as a Python package. Each of these tools can then be joined together to build up a pipeline for a specific situation. 

There are two basic configuration files required

* Snakefile - configures the snakemake workflow system
* config.yaml - provides input options for the individual configurations

These files are best stored in ./configs/<sub-directory>/ (under version control) and then softlinked into the root directory.

## Documentation

Documentation for KAPy is contained in the `docs` folder. 
* [Background.md](./docs/Background.md) - Background knowledge useful for getting started with KAPy.
* [Configuration.md](./docs/Configuration.md) - Details the configuration system and options available in KAPy.

## Contributing

KAPy is in active development and welcomes all contributions, both large and small.  is being used in production by climate services specialists around the world.
    
* If you have a suggestion for a new feature or want to report a bug, please file an issue via the issue tracker.
* If you would like to contribute code or documentation, check out the [Contributing Guidelines](./docs/CONTRIBUTING.md) before you begin!

## How to cite KAPy

If you wish to cite KAPy in your work, please cite this repository (https://github.com/Klimaatlas/KAPy/) and the push hash. A publication describing KAPy will be prepared in the future.

## License

KAPy is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License. A copy of this license is provided in the `docs` folder ([LICENSE](./docs/LICENSE)).
    
## Code of Conduct

A code of conduct for the KAPy community is found in [`docs/CODE_OF_CONDUCT.md`](./docs/CODE_OF_CONDUCT.md). In short: be kind.
    
## Credits
    
The development of KAPy is financed via a grant from the Danish Central Government to  the Danish Meterological Institute.    
    
## Why KAPy?

KAPy takes its name from joining the KA from DMI's *Klimaatlas* with the Py from Python, in the style of many Python libraries. 

More importantly, the name is also a homonym for the phrase *ka pai* from *Te Reo Maori*, the language of the Maori people, the *tangata whenua* (indigenous people) of Aotearoa New Zealand. The phrase means simply "good", but can also be used as praise, as in "well done". e.g.

```
Son: Look dad! I made a Klimaatlas in Python!
Dad: Ka pai, son, ka pai!
```
