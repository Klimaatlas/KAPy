# KAPy
Klimaatlas in Python

The goal of KAPy is to create an open-source and flexible framework that can be used to generate Klimaatlas-like analyses anywhere in the world, from both CMIP and CORDEX datasets. KAPy is therefore a ground-up python-based rethink of the original Klimaatlas Denmark pipeline.

## Getting Started

KAPy is based on a small set of fundamental technologies that form the core of the processing. These are as follows
* xarray - for storing and working with datasets. dask is use closely in conjunction with xarray
* xclim - for generating climate indicies
* snakemake (?) - for workflow control
* ESGF package (?) - for searching ESGF repositories

## Workflow

KAPy is structured around a central package of tools, collated together as a Python package. Each of these tools can then be joined together to build up a pipeline for a specific situation. A local configuration file also takes care of the specifics configuration in each case.

## Why KAPy?

KAPy takes its name from joining the KA from Klimaatlas with the Py from Python, in the style of many Python libraries. 

More importantly, the name is also a homonym for the phrase *ka pai*, taken from the language of the Maori people, the *tangata whenua* (indigenous people) of Aotearoa New Zealand. The phrase means simply "good", and can also be used as praise, as in "well done".
