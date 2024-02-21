# KAPy - *Klimaatlases* in Python

KAPy is an open-source and flexible framework that can be used to generate climate indicators anywhere in the world, working from both CMIP and CORDEX datasets. KAPy is a ground-up python-based rethink of the pipeline originally developed to power the Danish Meterological Institute's *Klimaatlas* climate service.

## Getting started

Here we describe the basic steps to install and configure KAPy. Start by cloning the latest version of the code from the repository:

```
git clone https://github.com/Klimaatlas/KAPy.git
```
Alternatively, if you don't have git installed, you can also download the source-code of the latest release from [https://github.com/Klimaatlas/KAPy/releases] or of the very latest version from [https://github.com/Klimaatlas/KAPy/archive/refs/heads/main.zip]. In either case, unzip the downloaded file to an appropriate location and you've got yourself a copy of KAPy.

Next, we need to setup the Python environment, containing the packages used by KAPy. Add-on libraries in Python are referred to as "packages" and their installation is maintained by a package manager, of which there are many to choose from (e.g. Anaconda, Conda, Miniconda, Mamba, Micromamba etc). The example code given here is for Conda - you can download it from https://conda.io/projects/conda/en/latest/index.html if you don't have it already, but KAPy should work just as well with other package managers.

A list of packages required to run KAPy can be found in the file `./configs/eny.yaml`. In the case of Conda, this list can be used to create an environment as follows:

```
conda env create -f ./configs/env.yaml
```

The resulting environment (called `KAPy`) is a self-contained setup that has everything necessary to run KAPy. Prior to useage, it needs to be activated using:

```
conda activate KAPy
```

KAPy is configured via a configuration file, `config.yaml`, in the project base directory. Some example configuration files are stored in the folder `./configs` and can be either copied or soft-linked into the project root folder. The tutorials contained with this documentation can be configured like so:

```
cp configs/tutorials/config.yaml .
```

Note that `config.yaml` files in the project directory are ignored by git, to avoid potential conflicts between users with different configurations.

Finally, a small setup script can be used to generate the necessary output directories:

```
python ./Setup.py
```

And so you're ready to go. For getting familar with the workings of KAPy, we recommend looking at the document listed below, and particularly the tutorials.

## Documentation

Documentation for KAPy is contained in the `./docs` folder. 
* [KAPY_concepts.md](./docs/KAPy_concepts.md) - Explains key concepts and definitions used in KAPy.
* [Tutorials](./docs/tutorials/README.md) - Worked tutorials for getting to know KAPy better.
* [Background.md](./docs/Background.md) - Background knowledge useful for getting started with KAPy.
* [Configuration.md](./docs/Configuration.md) - Details the configuration system and options available in KAPy.

## Contributing

KAPy is in active development and welcomes all contributions, both large and small.  
    
* If you have a suggestion for a new feature or want to report a bug, please file an issue via the issue tracker.
* If you would like to contribute code or documentation, check out the [Contributing Guidelines](./docs/Contributing.md) before you begin!

## How to cite KAPy

If you wish to cite KAPy in your work, please cite this repository (https://github.com/Klimaatlas/KAPy/) and the release version. A publication describing KAPy will be prepared in the future.

## License

KAPy is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License. A copy of this license is provided in the `docs` folder ([LICENSE](./docs/LICENSE)).
    
## Code of Conduct

A code of conduct for the KAPy community is found in the [Code of Conduct](./docs/Code_of_conduct.md). In short: be kind.
    
## Credits
    
The development of KAPy is financed via a grant from the Danish Central Government to the Danish Meterological Institute.    
    
## Why KAPy?

KAPy takes its name from joining the KA from DMI's *Klimaatlas* with the Py from Python, in the style of many Python libraries. 

More importantly, the name is also a homonym for the phrase *ka pai* from *Te Reo Maori*, the language of the Maori people, the *tangata whenua* (indigenous people) of Aotearoa New Zealand. The phrase means simply "good", but can also be used as praise, as in "well done". e.g.

```
Son: Look dad! I made a Klimaatlas in Python!
Dad: Ka pai, son, ka pai!
```
