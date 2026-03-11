"""
#Setup for debugging with VS code 
import os
print(os.getcwd())
os.chdir("KAPy/workflow")
import KAPy
os.chdir("../..")
config=KAPy.getConfig("./config/config.yaml")  
wf=KAPy.getWorkflow(config)
outFile=[list(wf['ensstats'].keys())[7]]
inFiles=wf['ensstats'][outFile[0]]
%matplotlib inline
"""

import xarray as xr
import numpy as np

def generateEnsstats(outFile, inFiles, percentiles,method):
    # Setup the ensemble
    # Given that all input files have been regridded onto a common grid,
    # they can then be concatenated into a single object. There are
    # two approachs. Previously we have used the create_ensemble from xclim.ensembles
    # However, this is quite fancy, and does a lot of logic about calendars that
    # create further problems. It also doesn't seem to handle cftime calendars at all well,
    # nor propigate attributes cleanly.
    # Instead, we do it all manually by directly opening the files with open_mfdataset, and then
    # loading it into ram
    time_coder = xr.coders.CFDatetimeCoder(use_cftime=True)
    thisEns = xr.open_mfdataset(inFiles, 
                                concat_dim="realization", 
                                combine="nested",
                                coords="all",
                                decode_times=time_coder,
                                decode_timedelta=False)
    thisEns=thisEns.compute()

    #Function to rename ensemble statistics once generated
    def renameEnsStats(d,suffix):
        for n in ['indicator','delta']:
            d=d.rename({f"{n}" : f"{n}_{suffix}"})
        return d

    #Calculate number of ensemble members at each point
    ensN=(~np.isnan(thisEns)).sum(dim="realization",keep_attrs=True)
    ensN=renameEnsStats(ensN,"n")
    
    # Calculate the statistics
    ensMean= thisEns.mean(dim="realization",keep_attrs=True)
    ensMean=renameEnsStats(ensMean,"mean")
    ensSd= thisEns.std(dim="realization",keep_attrs=True)
    ensSd=renameEnsStats(ensSd,"stdev")
    ensMax= thisEns.max(dim="realization",keep_attrs=True)
    ensMax=renameEnsStats(ensMax,"max")
    ensMin= thisEns.min(dim="realization",keep_attrs=True)
    ensMin=renameEnsStats(ensMin,"min")

    #Calculate the percentiles and transpose to a more friendly order
    ptileList=sorted(percentiles)
    qtileList=[x/100 for x in ptileList]
    ensPercs=thisEns.quantile(q=qtileList, dim='realization',method=method,keep_attrs=True)
    ensPercs=ensPercs.rename({"quantile":"percentiles"})
    ensPercs=ensPercs.assign_coords(percentiles=ptileList)
    
    if "periodID" in ensPercs.indicator.dims:
        ensPercs=ensPercs.transpose("periodID","seasonID","percentiles",...)
    else:
        ensPercs=ensPercs.transpose("time","seasonID","percentiles",...)
    ensPercs=renameEnsStats(ensPercs,"percentiles")

    # Combine results and sort
    ensOut = xr.merge([ensPercs,ensMean,ensSd,ensN,ensMax,ensMin])
    sorted_vars = sorted(ensOut.data_vars)  # Get sorted variable names
    ensOut = ensOut[sorted_vars]  # Reorder dataset

    #Make sure that we reapply the attributes and auxillary coordinates as well, which have a
    #habit of getting lost along the way. Note that we also need to average
    #over these coordinates, as there is in principle one for each realization
    auxCoords={key: thisEns.coords[key].mean(dim="realization") for key in thisEns.coords if key not in ensOut.dims}
    ensOut = ensOut.assign_coords(auxCoords)
    ensOut.attrs=thisEns.attrs

    #Write out
    ensOut.to_netcdf(outFile[0])
