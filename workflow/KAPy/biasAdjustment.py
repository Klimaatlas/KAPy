import xarray as xr
import tempfile
import xesmf as xe
import json
from . import helpers
#from dask.distributed import Client


"""
#Setup for debugging 
import os
print(os.getcwd())
os.chdir("KAPy/workflow")
import KAPy
import KAPy.helpers as helpers
os.chdir("../..")
config=KAPy.getConfig("./config/config.yaml")  
config=KAPy.getConfig("./workflow/testing/config.yaml")
wf=KAPy.getWorkflow(config)
thisCal='tas-ba'
outFile=list(wf['bias_adj'][thisCal]['input_dict'].keys())[0]
target_file=   wf['bias_adj'][thisCal]['input_dict'][outFile]['target']
reference_file=wf['bias_adj'][thisCal]['input_dict'][outFile]['ref']
tempDir=config['dirs']['tempDir']
outputGrid=config['biasAdjustment'][thisCal]['outputGrid']
trainPeriodStart=config['biasAdjustment'][thisCal]['trainPeriodStart']
trainPeriodEnd=config['biasAdjustment'][thisCal]['trainPeriodEnd']
baVariable=config['biasAdjustment'][thisCal]['baVariable']
method=config['biasAdjustment'][thisCal]['method']
grouping=config['biasAdjustment'][thisCal]['grouping']
additionalArgs=config['biasAdjustment'][thisCal]['additionalArgs']
import matplotlib.pyplot as plt
%matplotlib inline
"""


def biasAdjust(target_file,reference_file,tempDir,outputGrid,trainPeriodStart,trainPeriodEnd,baVariable,method,grouping,
              additionalArgs,customScriptPath,customScriptFunction,**kwargs):
    # We choose to use a simplified typology here, where we have a target dataset that needs to be
    # be bias-adjusted to match the climatology of the reference dataset. In the Xclim typology,
    # "target" corresponds to "hist" and "sim" in one file. "ref" remains the same.
    # The general strategy employed is as follows:
    # * Regrid so that everything is on the same (user defined)
    # * Merge target and ref into one dataset object. This requires a degree of
    #   massaging of the time units to make sure everything is comparable
    # * Apply the bias-adjustment function to chunks of the combined dataset using dask

    #Setup ------------------------
    target=helpers.readFile(target_file)
    reference=helpers.readFile(reference_file)
 #   client=Client()
  #  print(client.dashboard_link)
    
    # Regrid to common spatial grids ------------------
    # Regrid target using nearest neighbour interpolation to the appropriate grid. 
    # We have tried several iterations of this based on CDO, but CDO unfortunately doesn't
    # respect the chunking of the target file. xESMF is currently our tool of choice
    # due to its ability to work ok with dask.
    # The output grid is configurable set choices accordingly
    if outputGrid=="reference":
        from_this_grid=target
        to_this_grid=reference
    elif outputGrid=="target":
        from_this_grid=reference
        to_this_grid=target
    else:
        raise ValueError(f"Unknown output grid option, '{outputGrid}' supplied to  biasAdjust function.")
    # Start by getting the regridding weights
    regrdWtsFname=tempfile.NamedTemporaryFile(dir=tempDir,
                                                delete=False,
                                                prefix="regrdWts_",
                                                suffix=".nc").name
    regrdr=xe.Regridder(ds_in=from_this_grid,
                        ds_out=to_this_grid,
                       method="nearest_s2d",
                       filename=regrdWtsFname,
                       unmapped_to_nan=True)
    # Then apply the regridding. 
    # The regridder seems to work best when it can work with all of the spatial elements 
    # together, implying full spatial chunking. But this creates problems with the later
    # steps of the bias adjustment, which require that we have the full timeseries in memory.
    # We therefore choose to write the regridding data to disk at this point with a 
    # chunking pattern that is amenable to further work downstrem. 
    spatial_chunks={d: -1 for d in from_this_grid.dims if d!='time'}
    rechunked=from_this_grid.chunk(spatial_chunks)
    regridded_filename=tempfile.NamedTemporaryFile(dir=tempDir,
                                                delete=False,
                                                prefix="regridded_",
                                                suffix=".nc").name
    regridded=regrdr(rechunked,output_chunks=(-1,-1),keep_attrs=True)
    chunkThisWay=[min([256,16,16][i],regridded.shape[i]) for i in range(0,3)]
    regridded.to_netcdf(regridded_filename,
              encoding={regridded.name:{'chunksizes':chunkThisWay}})

    #Now reopen with a time-oriented chunking - one file will be the source 
    #file, the other will be the regridded file.
    if outputGrid=="reference":
        target=helpers.readFile(regridded_filename,chunks={'time':-1}).unify_chunks()
        reference=helpers.readFile(reference_file,chunks={'time':-1}).unify_chunks()
    elif outputGrid=="target":
        target=helpers.readFile(target_file,chunks={'time':-1}).unify_chunks()
        reference=helpers.readFile(regridded_filename,chunks={'time':-1}).unify_chunks()

    # Prepare combined dataset ------------------------------
    # From a bias-adjustment perspective, the only part of the reference dataset that
    # is interesting is the common period data - there could be a whole lot more
    # that we otherwise don't use. We therefore drop the uninteresting parts
    reference_common=helpers.timeslice(reference,trainPeriodStart,trainPeriodEnd)
    if reference_common.time.size==0:
        raise ValueError(f"The selected training period from {trainPeriodStart} to {trainPeriodEnd} does not overlap with the reference dataset, which runs from {reference.time.to_index()[0].strftime("%Y-%m-%d")} to {reference.time.to_index()[-1].strftime("%Y-%m-%d")}")
    # Merge into one dataset object, with common spatial dimensions but
    # differentiated time dimensions. Note the need to unify the chunking
    reference_common=reference_common.rename({"time": "reftime"})
    combDS2=xr.Dataset({'target':target.unify_chunks(),
                        'ref':reference_common.unify_chunks()})
    combDS=combDS2.unify_chunks()

    #Parallelised bias adjustment functions ------------------------------
    def biasAdjustThisChunk(chnk,trainPeriodStart,trainPeriodEnd,
                           method,additionalArgs,grouping):
        #Debug
        # tg=combDS.target.data.blocks[0,0,0]
        # rfTP=combDS.ref.data.blocks[0,0,0]
        #Extract the data from the input block
        tg=chnk.target
        rfTP=chnk.ref

        #Truncate time slice to the common training period (TP). 
        #Adjust the naming of the reference time
        tgTP=helpers.timeslice(tg,trainPeriodStart,trainPeriodEnd)
        rfTP=rfTP.rename({"reftime": "time"})

        #Match calendars between reference data and simulations
        #Note that here we have chosen here to align on year when converting to/from
        #a 360 day calendar. This follows the recommendation in the xarray documentaion,
        #under the assumption that we are primarily going to be working with daily data.
        #See here for details:
        #https://docs.xarray.dev/en/stable/generated/xarray.Dataset.convert_calendar.html
        tgTP=tgTP.convert_calendar(rfTP.time.dt.calendar,
                                    use_cftime=True,
                                    align_on="year")  
        
        #We interpolate time to be on a common time axis
        tgTP=tgTP.interp(time=rfTP.time,method="nearest")
        
        #Setup mapping to grouping
        if grouping=="none":
            groupThisWay="time"
        else:
            groupThisWay="time."+grouping
        
        #Apply method
        if method=="xsdba-eqm":
            #Empirical quantile mapping -----------------------------
            from xsdba.adjustment import EmpiricalQuantileMapping
            EQM = EmpiricalQuantileMapping.train(rfTP, 
                                                    tgTP, 
                                                    group=groupThisWay,
                                                    **additionalArgs)
            res = EQM.adjust(tg, extrapolation="constant", interp="nearest")

        elif method=="xsdba-dqm":
            #Detrended quantile mapping -----------------------------
            from xsdba.adjustment import DetrendedQuantileMapping
            DQM = DetrendedQuantileMapping.train(rfTP, 
                                                    tgTP, 
                                                    group=groupThisWay,
                                                    **additionalArgs)
            res = DQM.adjust(tg, extrapolation="constant", interp="nearest")

        elif method=="xsdba-scaling":
            #Xclim - Scaling--------------------------------
            from xsdba.adjustment import Scaling
            this = Scaling.train(rfTP, 
                                    tgTP,
                                    group=groupThisWay,
                                    **additionalArgs)
            res = this.adjust(tg, interp="nearest")

        elif method=="custom":
            raise ValueError('"custom" bias adjustment functions are currently not implemented')
        
        else:
            #Custom defined function
            raise ValueError(f'Unsupported bias adjustment method "{method}".')
        
        #Correct output structure and Finish
        resTrans = res.transpose(*rfTP.dims)
        return resTrans
    
    # Do bias adjustment----------------------
    # Apply function in a parallelised manner. 
    calCfg={"trainPeriodStart":trainPeriodStart,
                                "trainPeriodEnd":trainPeriodEnd,
                                "grouping":grouping,
                                "method":method,
                                "additionalArgs":additionalArgs}
    out=xr.map_blocks(func=biasAdjustThisChunk,
                        obj=combDS,
                        kwargs=calCfg,
                        template=target)

    #Finishing touches
    out2 = out.assign_attrs({"biasAdjustment_args": json.dumps(calCfg)})

    return out2
