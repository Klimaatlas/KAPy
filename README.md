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


## Background knowledge

KAPy is based on a small set of fundamental technologies that form the core of the processing. These are as follows:

* Python 3 - as the primary coding language. 
* snakemake - for workflow control
* xarray - for storing and working with datasets. dask is use closely in conjunction with xarray
* xclim - for generating climate indicies

It is not necessary to be familar with all of these tools in order to be able to use KAPy - in principle it should be possible to simply configure it and run it. In reality, most users will anyway want to dive deeper into the code, and therefore require a working knowledge of many of these libraries. The following tutorials are suggested as good learning resources if you are not already familar with them - a basic familiarity with Python is also assumed.

### Snakemake

Snakemake provides workflow coordinating and monitoring for KAPy. Snakemake can be understood as an analogue of GNU Make, which many will be familar with from installing software in Linux and Unix environments.  The KAPy pipeline is defined as a series of rules in Snakemake's python-based language (see the "Snakefile") describing how to make an output and the inputs it requires - Snakemake then takes care of applying these rules in the apppropriate order. Like GNU Make, Snakemake checks for  rules and files that have already been processed, and only handles missing targets (including upstream dependencies). In this way, adding a new member to an ensemble, for example, only requires processing of the new files (and not all files in the ensemble). You can learn more about Snakemake in the following resources:

* The Snakemake "rolling" paper - https://f1000research.com/articles/10-33/v2
* The Snakemake tutorial - https://snakemake.readthedocs.io/en/stable/tutorial/tutorial.html#tutorial
* Snakemake documentation - https://snakemake.readthedocs.io/en/stable/

### Xarray

Xarray works as the core class for working with climate data (specificially NetCDF files) in KAPy. KAPy works on a file-to-file basis, where each step of the processing chain involves reading one or more files, performing some computations on it, and then writing the results out to a subsequent file that can be picked up by subsequent steps. Xarray is the backbone of these process, providing objects representing the on-disk files in python and taking care of reading, processing and writing outputs again. The following resources are recommended

* the xarray article - https://openresearchsoftware.metajnl.com/articles/10.5334/jors.148
* xarray "Getting Started" guide - https://docs.xarray.dev/en/latest/getting-started-guide/index.html
* the Xarray tutorial - https://tutorial.xarray.dev/intro.html
* xarray also has a good set of Tutorials and Videos that are worth exploring - https://docs.xarray.dev/en/stable/tutorials-and-videos.html

### Xclim

Xclim provides a series of "pre-packaged" functions to calculate climate indicators from input climate variables. It is based on the Xarray package and therefore fits cleanly into the KAPy chain. Relevant resources for learning more about Xclim include:

* Xclim documentation - https://xclim.readthedocs.io/en/stable/

### Additional tools

The following tools also make an important contribution to the KAPy pipeline, but a detailed understanding of their mechanics is not necessary in most cases. 

* esgf-pyclient - for searching ESGF repositories. 
* pydap for interfaceing with ESGF via the OpenDAP protocol
* dask - helps spread the work across multiple processors, when available
* R - a subset of KAPy components are coded in R, but the intention that these should be used as standalone tools


## Workflow

KAPy is structured around a central package of tools, collated together as a Python package. Each of these tools can then be joined together to build up a pipeline for a specific situation. 

There are two basic configuration files required

* Snakefile - configures the snakemake workflow system
* config.yaml - provides input options for the individual configurations

These files are best stored in ./configs/<sub-directory>/ (under version control) and then softlinked into the root directory.
    

## Why KAPy?

KAPy takes its name from joining the KA from DMI's *Klimaatlas* with the Py from Python, in the style of many Python libraries. 

More importantly, the name is also a homonym for the phrase *ka pai* from *Te Reo Maori*, the language of the Maori people, the *tangata whenua* (indigenous people) of Aotearoa New Zealand. The phrase means simply "good", but can also be used as praise, as in "well done". e.g.

```
Son: Look dad! I made a Klimaatlas in Python!
Dad: Ka pai, son, ka pai!
```
