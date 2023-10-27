# Background knowledge

KAPy is based on a small set of fundamental technologies that form the core of the processing. These are as follows:

* Python 3 - as the primary coding language. 
* snakemake - for workflow control
* xarray - for storing and working with datasets. dask is use closely in conjunction with xarray
* xclim - for generating climate indicies

It is not necessary to be familar with all of these tools in order to be able to use KAPy - in principle it should be possible to simply configure it and run it. In reality, most users will anyway want to dive deeper into the code, and therefore require a working knowledge of many of these libraries. The following tutorials are suggested as good learning resources if you are not already familar with them - a basic familiarity with Python is also assumed.

## Snakemake

Snakemake provides workflow coordinating and monitoring for KAPy. Snakemake can be understood as an analogue of GNU Make, which many will be familar with from installing software in Linux and Unix environments.  The KAPy pipeline is defined as a series of rules in Snakemake's python-based language (see the "Snakefile") describing how to make an output and the inputs it requires - Snakemake then takes care of applying these rules in the apppropriate order. Like GNU Make, Snakemake checks for  rules and files that have already been processed, and only handles missing targets (including upstream dependencies). In this way, adding a new member to an ensemble, for example, only requires processing of the new files (and not all files in the ensemble). You can learn more about Snakemake in the following resources:

* The Snakemake "rolling" paper - https://f1000research.com/articles/10-33/v2
* The Snakemake tutorial - https://snakemake.readthedocs.io/en/stable/tutorial/tutorial.html#tutorial
* Snakemake documentation - https://snakemake.readthedocs.io/en/stable/

## Xarray

Xarray works as the core class for working with climate data (specificially NetCDF files) in KAPy. KAPy works on a file-to-file basis, where each step of the processing chain involves reading one or more files, performing some computations on it, and then writing the results out to a subsequent file that can be picked up by subsequent steps. Xarray is the backbone of these process, providing objects representing the on-disk files in python and taking care of reading, processing and writing outputs again. The following resources are recommended

* the xarray article - https://openresearchsoftware.metajnl.com/articles/10.5334/jors.148
* xarray "Getting Started" guide - https://docs.xarray.dev/en/latest/getting-started-guide/index.html
* the Xarray tutorial - https://tutorial.xarray.dev/intro.html
* xarray also has a good set of Tutorials and Videos that are worth exploring - https://docs.xarray.dev/en/stable/tutorials-and-videos.html

## Xclim

Xclim provides a series of "pre-packaged" functions to calculate climate indicators from input climate variables. It is based on the Xarray package and therefore fits cleanly into the KAPy chain. Relevant resources for learning more about Xclim include:

* Xclim documentation - https://xclim.readthedocs.io/en/stable/

## Additional tools

The following tools also make an important contribution to the KAPy pipeline, but a detailed understanding of their mechanics is not necessary in most cases. 

* esgf-pyclient - for searching ESGF repositories. 
* pydap for interfaceing with ESGF via the OpenDAP protocol
* dask - helps spread the work across multiple processors, when available
* R - a subset of KAPy components are coded in R, but the intention that these should be used as standalone tools


