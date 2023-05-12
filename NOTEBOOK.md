# 2023.05.12
Integrated Snakemake. Wrapped download up into a function. First successful mass downloads. 
* Next develop a strategy of processing. Time periods? Or annual time series?
* Add independent credentials configuration in separate file?
* Tidy up ESGF search
* Add Ancient to downloaded files

# 2023.05.11
Got authentication working with pydap, and can now download via DAP! It works
* [Y] Handle lon-lat subsetting more robustly, particularly around rlon vs lon
* [Y] Wrap download script up into a function
* [Y] Rebuild configuration system
* [Y] Integrate with snakemake

# 2023.05.08
First working version, managed to get some data downloaded using OpenDAP. Yah!
* [Y] Look at the authentication for downloading from CORDEX - not sure that logon manager is really working as it should there. But the problem may also be simply with the configuration of the server - switching to another file on another server seemed to help.