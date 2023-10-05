TODO:
* Add explicit declaration of xarray groupings
* Creation of xarray object should incorporate spatial domain
* Bug report (?) about seg fault in regrdding?
* Handle indicators requiring multiple variables
* Add documentation
* Streamline makefile linkages

# 2023.10.05
Added multiple time-averaging schemes. Testing on ocean data. Looking good

# 2023.10.03
Good progress in the last couple of days generalising the script to be configurable through YAML files throughout. Regridding seems to be causing some odd problems to be investigated next.

# 2023.09.29
Made some progress in restarting work on KAPy. Established a configuration setup with system-wide defaults and the ability to override for individual instances. Setup a DK instance to work with raw files.

# 2023.06.15
Doing the ensemble statistics was tricky - struck a problem with numerical precision in the coordinate axes being different making it nearly impossible to get the data to merge. Solved by regridding everything (AFR-22 and AFR-44) to a common 0.1 degree grid. Making the notesbooks in R went much better and now have the first results for KAGH! Whoo-hoo!

# 2023.06.14 
Got index101 working with snakemake. now to calculate ensemble statistics

# 2023.06.13 
Got index101 working for a single file. Now integrate into snakemake. Then generate ensemble statistics and we're there!

# 2023.05.24
Better progress today. Able to generate xarray datasets and write them to pickles. Now working on a function to group them into dataset objects for processing by xclim.

# 2023.05.22 
Some progress making a function to generate an xarray object from a database. But slow going generally. Downloaded most of the files, but check status

# 2023.05.12
Integrated Snakemake. Wrapped download up into a function. First successful mass downloads. 
* Next develop a strategy of processing. Time periods? Or annual time series?
* Add independent credentials configuration in separate file?
* Tidy up ESGF search
* Add Ancient to downloaded files
* Add reports

# 2023.05.11
Got authentication working with pydap, and can now download via DAP! It works
* [Y] Handle lon-lat subsetting more robustly, particularly around rlon vs lon
* [Y] Wrap download script up into a function
* [Y] Rebuild configuration system
* [Y] Integrate with snakemake

# 2023.05.08
First working version, managed to get some data downloaded using OpenDAP. Yah!
* [Y] Look at the authentication for downloading from CORDEX - not sure that logon manager is really working as it should there. But the problem may also be simply with the configuration of the server - switching to another file on another server seemed to help.
