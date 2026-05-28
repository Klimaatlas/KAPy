from dask.distributed import Client, LocalCluster
from inspect import signature
from humanfriendly import parse_size
import logging
import os

# Assert that we are supplied with at least the following resource definitions
#  * threads
#  * mem, mem_mb or mem_mib
# Throw an error if these are missing. Other resources can be handled


def setupDaskCluster(threads,
                     resources):

    logging.getLogger("distributed").setLevel(logging.WARNING)

    # Prevent nested threading leading to oversubscription
    # ChatGPT is very insistent about this being a good idea.
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"

    #Switch between type of dask 
    daskArgs=dict(resources)
    daskType=daskArgs.get("dask","")

    #----- local Cluster
    if daskType.upper()=="LOCALCLUSTER":
        #Agree on how much memory we actually have
        #Memory resources can be defined from "mem","mem_mib" or "mem_mib"
        #We take the most conservative memory useage. If nothing is defined, throw an error
        memList=[]
        if "mem" in daskArgs:
            memList.append(daskArgs.get("mem"))
        if "mem_mb" in daskArgs:
            memList.append(parse_size(f"{daskArgs.get("mem_mb")}MB"))
        if "mem_mib" in daskArgs:
            memList.append(parse_size(f"{daskArgs.get("mem_mb")}MiB"))
        if not memList:
            raise ValueError("Use of dask LocalCluster requires the specification of total memory useage but it cannot be inferred from the supplied arguments. Please specify at least one of 'mem', 'mem_mb' or 'mem_mib' in the snakemake profile.")
        mem=min(memList)

        #Agree on the number of workers.
        #There are at least three possible ways to define the number of workers. Again, we consider all approaches
        #as possible constraints, and then take the lowest number
        #1. From threads and threads_per_worker.
        #   If threads_per_worker is not specified, assume 1
        nWorkerList=[int(threads/daskArgs.get("threads_per_worker",1))]
        #2. n_workers is specified directly as a resource
        if "n_workers" in daskArgs:
            nWorkerList.append(daskArgs.get("n_workers"))
        #3. Inferred from the memory and memory per worker (memory_limit)
        #   However, don't want to accept "auto" or "0", which are valid arguments to memory_limit
        if "memory_limit" in daskArgs:
            memLim=daskArgs.get("memory_limit")
            if memLim in ['auto','0',0, None]:
                raise ValueError(f"Supplied 'memory_limit' argument '{memLim}', while valid for LocalCluster(), is not allowed in KAPy.")
            nWorkerList.append(int(mem/parse_size(daskArgs.get("memory_limit"))))
        #Take the minimum
        nWorkers=min(nWorkerList)
        
        #Now that we have the number of workers that are supported, we can then calculate the memory per worker.
        #Again, this can be done in multiple ways.
        #1. Calculate from the number of workers
        memLimList=[mem/nWorkers]
        #2. Can also be specified
        if "memory_limit" in daskArgs:
            memLimList.append(parse_size(daskArgs.get("memory_limit")))
        #Choose the lowest
        memLim=min(memLimList)

        #Populate the arguments to LocalCluster(), using the function signature itself as inspiration
        lcFunctionArgs = signature(LocalCluster).parameters
        lcArgs = {k: v for k, v in daskArgs.items() if k in lcFunctionArgs }
        lcArgs['n_workers']=nWorkers
        lcArgs['memory_limit']=memLim

        #Configure localCluster
        cluster = LocalCluster(**lcArgs)
        client = Client(cluster)

        #Save logs
        logger = logging.getLogger(__name__)
        logger.info("Dask client configuration: %s", client)
        logger.info("Dashboard address: %s", client.dashboard_link)

        return client
    
    #---- No dask
    else:
        return None
    