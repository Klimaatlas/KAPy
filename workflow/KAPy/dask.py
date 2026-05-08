from dask.distributed import Client, LocalCluster
import os

def setupDask(nWorkers=None,threadsPerWorker=None,memoryLimit=None):

    # Prevent nested threading leading to oversubscription
    # ChatGPT is very insistent about this being a good idea.
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"

    # Setup cluster
    # Note the handling of values if not specified is as follows (based on LocalCluster definition:
    # https://docs.dask.org/en/stable/deploying-python.html#reference)
    # * n_workers: default is None
    # * threads_per_worker: default is None
    # * memory_limit: None 

    cluster = LocalCluster(
        n_workers=nWorkers,
        threads_per_worker=threadsPerWorker,
        memory_limit=f"{memoryLimit/nWorkers}MB",
    )

    client = Client(cluster)

    print(cluster)

    return client