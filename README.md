# KAPy
Klimaatlas in Python

The goal of KAPy is to create an open-source and flexible framework that can be used to generate Klimaatlas-like analyses anywhere in the world, from both CMIP and CORDEX datasets. KAPy is therefore a ground-up python-based rethink of the original Klimaatlas Denmark pipeline.

## Getting Started

KAPy is based on a small set of fundamental technologies that form the core of the processing. These are as follows
* snakemake - for workflow control
* xarray - for storing and working with datasets. dask is use closely in conjunction with xarray
* xclim - for generating climate indicies
* esgf-pyclient - for searching ESGF repositories. https://esgf-pyclient.readthedocs.io/
* pydap for interfaceing with ESGF via the OpenDAP protocol

## Workflow

KAPy is structured around a central package of tools, collated together as a Python package. Each of these tools can then be joined together to build up a pipeline for a specific situation. 

There are two basic configuration files required
* Snakefile - configures the snakemake workflow system
* config.yaml - provides input options for the individual configurations

These files are best stored in ./configs/<sub-directory>/ (under version control) and then softlinked into the root directory.


## Why KAPy?

KAPy takes its name from joining the KA from Klimaatlas with the Py from Python, in the style of many Python libraries. 

More importantly, the name is also a homonym for the phrase *ka pai*, from *Te Reo Maori*, the language of the Maori people, the *tangata whenua* (indigenous people) of Aotearoa New Zealand. The phrase means simply "good", but can also be used as praise, as in "well done", and as "thank you" too.
