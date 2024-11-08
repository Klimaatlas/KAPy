# KAPy - *Klimaatlases* in Python

KAPy is an open-source and flexible framework that can be used to generate climate indicators anywhere in the world, working from datasets such as CMIP and CORDEX together with observations. KAPy is a ground-up python-based rethink of the pipeline originally developed to power the Danish Meteorological Institute's *Klimaatlas* climate service, but is intended to be used more widely.

## Getting started

Here we describe the basic steps to install and configure KAPy. First, you need to get a copy of the KAPy source code onto the machine where you want to work. This is most easily done using git to clone the latest version of the code directly from the repository:
```
git clone git@github.com:Klimaatlas/KAPy.git
```
This approach also has the advantage of making it easy to get updates directly into your local folder. If you don't have git installed, you can download a zipped version of the source code directly from the website, here: https://github.com/Klimaatlas/KAPy/releases 

Next, we need to setup the Python environment containing the packages used by KAPy. Add-on libraries in Python are referred to as "packages" and their installation is maintained by a package manager, of which there are many to choose from (e.g. Anaconda, Conda, Miniconda, Mamba, Micromamba etc). The example code given here is for the Conda package manager - you can download it from https://conda.io/projects/conda/en/latest/index.html if you don't have it already, but KAPy should work just as well with other package managers. The examples are also for a Linux environment - however, a similar approach will hold if you want to try and get KAPy running in Windows.

A list of packages required to run KAPy can be found in the file [`./workflow/envs/env.yaml`](./workflow/envs/env.yaml). In the case of Conda, this list can be used to create an environment as follows:

```
conda env create --file ./workflow/envs/env.yaml
```

The resulting environment (called `KAPy`) is a self-contained setup that has everything necessary to run KAPy. The KAPy environment needs to be activated prior to use:

```
conda activate KAPy
```

And so you're ready to go. To get familiar with the workings of KAPy, we recommend looking at the document listed below, and particularly the [Tutorials](./docs/tutorials/README.md).

In the future, you may need to update the environment to reflect changes. This can be done with:

```
conda env update --file ./workflow/envs/env.yaml --prune

```

or by deleting the environment and installing it again from scratch:

```
conda deactivate
conda env remove -n KAPy
conda env create --file ./workflow/envs/env.yaml
```


## Documentation

Documentation for KAPy is contained in the `./docs` folder. 
* [Tutorials](./docs/tutorials/README.md) - Worked tutorials for getting to know KAPy better.
* [Configuration](./docs/Configuration.md) - Details the configuration system and options available in KAPy.
* [KAPy concepts](./docs/KAPy_concepts.md) - Explains key concepts and definitions used in KAPy.
* [Background](./docs/Background.md) - Background knowledge useful for getting started with KAPy.

## Contributing

KAPy is in active development and welcomes all contributions, both large and small.  
    
* If you have a suggestion for a new feature or want to report a bug, please file an issue via the issue tracker.
* If you would like to contribute code or documentation, check out the [Contributing Guidelines](./CONTRIBUTING.md) before you begin!

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
