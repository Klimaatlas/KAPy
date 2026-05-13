from dask.distributed import Client, LocalCluster
import logging
import os

def setupDaskCluster(nWorkers,
                     threadsPerWorker,
                     memoryPerWorker):

    logging.getLogger("distributed").setLevel(logging.WARNING)

    # Prevent nested threading leading to oversubscription
    # ChatGPT is very insistent about this being a good idea.
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"

    #Configure cluster
    cluster = LocalCluster(threads_per_worker=threadsPerWorker,
                           n_workers=nWorkers,
                           memory_limit=memoryPerWorker)

    #We're good. Make the client
    client = Client(cluster)

    #Save logs
    logger = logging.getLogger(__name__)
    logger.info("Dask client configuration: %s", client)
    logger.info("Dashboard address: %s", client.dashboard_link)

    return client