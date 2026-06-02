from dask.distributed import Client, LocalCluster
from inspect import signature
from humanfriendly import parse_size
import logging
import os

# Assert that we are supplied with at least the following resource definitions
#  * threads
#  * mem, mem_mb or mem_mib
# Throw an error if these are missing. Other resources can be handled
# Although resource handling is specified via the dask_resources table, the actual
# values that the rule gets apportioned can be overturned due to various processes,
# including the use of local profiles. The dask_resources table can be considered as
# the wish list - here we take what we actually have got and use it to build a cluster


def setupDaskCluster(threads, resources):

    logging.getLogger("distributed").setLevel(logging.WARNING)

    # Prevent nested threading leading to oversubscription
    # ChatGPT is very insistent about this being a good idea.
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"

    # Switch between type of dask
    resource_dict = dict(resources)

    # ----- local Cluster
    if "enabled" in resource_dict:
        # Agree on how much memory we actually have
        # Memory resources can be defined from "mem","mem_mib" or "mem_mib"
        # We take the most conservative memory useage. If nothing is defined, throw an error
        memList = []
        if "mem" in resource_dict:
            memList.append(parse_size(resource_dict.get("mem")))
        if "mem_mb" in resource_dict:
            memList.append(parse_size(f"{resource_dict.get("mem_mb")}MB"))
        if "mem_mib" in resource_dict:
            memList.append(parse_size(f"{resource_dict.get("mem_mb")}MiB"))
        if not memList:
            raise ValueError(
                "Use of dask LocalCluster requires the specification of total memory useage but it cannot be inferred from the supplied arguments. Please specify at least one of 'mem', 'mem_mb' or 'mem_mib' in the snakemake profile."
            )
        mem = min(memList)

        # Agree on the number of workers.
        # There are at least three possible ways to define the number of workers. Again, we consider all approaches
        # as possible constraints, and then take the lowest number
        # 1. From threads and threads_per_worker.
        #   If threads_per_worker is not specified, assume 1
        nWorkerList = [int(threads / int(resource_dict.get("threads_per_worker", 1)))]
        # 2. n_workers is specified directly as a resource
        if "n_workers" in resource_dict:
            nWorkerList.append(resource_dict.get("n_workers"))
        # 3. Inferred from the memory and memory per worker (memory_limit)
        #   However, don't want to accept "auto" or "0", which are valid arguments to memory_limit
        if "memory_limit" in resource_dict:
            memLim = resource_dict.get("memory_limit")
            if memLim in ["auto", "0", 0, None]:
                raise ValueError(
                    f"Supplied 'memory_limit' argument '{memLim}', while valid for LocalCluster(), is not allowed in KAPy."
                )
            nWorkerList.append(int(mem / parse_size(resource_dict.get("memory_limit"))))
        # Take the minimum
        nWorkers = min(nWorkerList)

        # Now that we have the number of workers that are supported, we can then calculate the memory per worker.
        # Again, this can be done in multiple ways.
        # 1. Calculate from the number of workers
        memLimList = [mem / nWorkers]
        # 2. Can also be specified
        if "memory_limit" in resource_dict:
            memLimList.append(parse_size(resource_dict.get("memory_limit")))
        # Choose the lowest
        memLim = min(memLimList)

        # Configure localCluster
        cluster = LocalCluster(
            n_workers=nWorkers,
            threads_per_worker=resource_dict.get("threads_per_worker"),
            memory_limit=memLim,
        )
        client = Client(cluster)

        # Save logs
        logger = logging.getLogger(__name__)
        logger.info("Dask client configuration: %s", client)
        logger.info("Dashboard address: %s", client.dashboard_link)

        return client

    # ---- No dask
    else:
        return None


def get_dask_threads(resource_table, family, id):
    # Check if the id or family are in the resource table
    if resource_table is None:
        return 1

    if id in resource_table:
        this = resource_table[id]
    elif family in resource_table:
        this = resource_table[family]
    else:
        return 1  # Default to a single thread

    # Extract from table
    return int(this["n_workers"]) * int(this["threads_per_worker"])


def get_dask_resources(resource_table, family, id):
    # Check if the id or family are in the resource table
    if resource_table is None:
        return {}

    if id in resource_table:
        this = resource_table[id]
    elif family in resource_table:
        this = resource_table[family]
    else:
        return {}  # Return an empty set

    # Infer memory requirement from table. But first disallow other memory_limit arguments
    memory_limit = this.get("memory_limit")
    if memory_limit in ["auto", "0", 0, None]:
        raise ValueError(
            f"Supplied 'memory_limit' argument '{memory_limit}', while valid for LocalCluster(), is not allowed in KAPy."
        )

    n_workers = int(this["n_workers"])
    mem = n_workers * parse_size(memory_limit)

    # Return dict
    rtn = {
        "enabled": this.get("enabled", None),
        "mem_mb": mem / 1e6,
        "n_workers": n_workers,
        "memory_limit": this.get("memory_limit"),
        "threads_per_worker": int(this.get("threads_per_worker")),
    }
    return rtn
