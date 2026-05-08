from dask.distributed import Client, LocalCluster
import logging
import os

def setupDaskCluster(host,
                     port,
                     nWorkers,
                     threadsPerWorker,
                     memLim):

    logging.getLogger("distributed").setLevel(logging.WARNING)

    try:
        #Try to connect to a client, to test if it exists
        #If successful, don't need to recreate
        client = Client(f"{host}:{port}", timeout="2s")

    except OSError:
        # Prevent nested threading leading to oversubscription
        # ChatGPT is very insistent about this being a good idea.
        os.environ["OMP_NUM_THREADS"] = "1"
        os.environ["MKL_NUM_THREADS"] = "1"
        os.environ["OPENBLAS_NUM_THREADS"] = "1"

        #Configure cluster
        if memLim is None:
            memoryPerWorker="auto"
        else:
            memoryPerWorker=f"{memLim/threadsPerWorker/nWorkers}MB"
        cluster = LocalCluster(scheduler_port=port,
                                host=host,
                            threads_per_worker=threadsPerWorker,
                            n_workers=nWorkers,
                            memory_limit=memoryPerWorker)
        client = Client(cluster)

    print(f"Dask client configuration: {client}")
    print(f"Dashboard address: {client.dashboard_link}")

    return client