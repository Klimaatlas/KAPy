import matplotlib.pyplot as plt
import xarray as xr
from pathlib import Path


def plot_and_save_change(model: str, indicator_id: str):

    cmip5_models = [
        "cnrm_aladin",
        "ecearth_cclm",
        "ecearth_hirham",
        "ecearth_rca",
        "hadgem_rca",
        "hadgem_remo",
        "mpi_cclm",
        "mpi_remo",
        "noresm_rca",
        "noresm_remo",
    ]
    cmip6_models = [
        "cnrm_hclim",
        "cnrm_racmo",
        "ecearth_racmo",
        "ecearthveg_cclm",
        "ecearthveg_hclim",
        "miroc_icon",
        "mpi_hclim",
        "mpi_icon",
        "mpi_racmo",
        "noresm_hclim",
    ]

    if model in cmip5_models:
        scenarios = ["rcp26", "rcp45"]
    elif model in cmip6_models:
        scenarios = ["ssp370"]
    else:
        print(f"\n'{model}' is not a valid model name\n")
        return

    path_to_netcdfs = Path(f"/lustre/storeC-ext/users/klimakverna/development/KAPy/results/7.netcdf/{model}")
    path_to_save_figures = Path(f"/lustre/storeC-ext/users/klimakverna/development/KAPy/testcase_1_results/{model}")
    files = [f"{path_to_netcdfs}/{indicator_id}_{scenario}_change_periods.nc" for scenario in scenarios]

    cmap = plt.cm.PuOr
    alpha = 0.8
    plot_variables = ["indicator_mean_change", "indicator_mean_relative_change"]
    plot_limits = [[-1e-5, 1e-5], [-20, 20]]
    periods = [2, 3]

    for sceanrio_idx, filename in enumerate(files):
        try:
            ds = xr.open_dataset(filename)
            print(ds)
        except FileNotFoundError:
            print(f"\nCan't find netcdf file '{filename}'\n")
            return

        for period in periods:
            for variable, limit in zip(plot_variables, plot_limits):
                plt.figure()
                ds[variable].sel(periodID=period).plot(
                    robust=True, vmin=limit[0], vmax=limit[-1], cmap=cmap, alpha=alpha
                )
                try:
                    plt.savefig(
                        f"{path_to_save_figures}/{indicator_id}_{scenarios[sceanrio_idx]}_{variable}_{model}_period_{period}"
                    )
                except FileNotFoundError:
                    print(
                        f"\nDidn't manage to save plot for model '{model}', indicator '{indicator_id}', "
                        f"scenario '{scenarios[sceanrio_idx]}', variable '{variable}' and period '{period}'. "
                        f"\nCheck that '{path_to_save_figures}' exists\n"
                    )


if __name__ == "__main__":
    model = "cnrm_hclim"
    indicator = "102"
    plot_and_save_change(model, indicator)
