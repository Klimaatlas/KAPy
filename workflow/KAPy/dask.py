from dask.distributed import Client, LocalCluster
from urllib.parse import urlparse
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

        #Check that resulting cluster is on the correct port
        actual = urlparse(cluster.scheduler_address)
        actual_port = actual.port
        print(actual_port)
        print(actual)
        if actual_port != port:
            raise RuntimeError(f"Cannot assign requested port: {port}")

        #We're good. Make the client
        client = Client(cluster)


    #Print some outputs
    print(f"Dask client configuration: {client}")
    print(f"Dashboard address: {client.dashboard_link}")

    return client