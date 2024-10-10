import csv
import matplotlib.pyplot as plt
from pathlib import Path
from glob import glob
import xarray as xr
from xclim import ensembles
import yaml
from KAPy.workflow.KAPy.save_change_to_netcdf import save_change_to_netcdf
from KAPy.workflow.KAPy.plots import makeBoxplot


def calculate_ensemble_mean(
    indicator_id: str, scenario: str, ensemble_filename: str | Path, config: dict, CMIP_version: None | int = None
):
    current_dir = Path(__file__).parent
    if "hist" not in scenario:
        periods = [2, 3]
        search_dir = current_dir / "results/7.netcdf"
        netcdf_files = glob(f"{search_dir}/**/{indicator_id}_{scenario}*.nc", recursive=True)
    else:
        periods = [1, 2, 3]
        search_dir = current_dir / "results/4.ensstats"

        match CMIP_version:
            case 6:
                netcdf_files = glob(f"{search_dir}/**/{indicator_id}_CMIP6_{scenario}*.nc", recursive=True)
            case 5:
                netcdf_files = glob(f"{search_dir}/**/{indicator_id}_CMIP5_{scenario}*.nc", recursive=True)
            case _:
                print("Invalid CMIP version")
                return

    ensemble_ds = xr.open_mfdataset(netcdf_files, concat_dim="realization", combine="nested")
    try:
        ensemble_ds = ensemble_ds.drop_vars(
            [
                "indicator_stdev",
                "indicator_min",
                "indicator_max",
                "indicator",
                "indicator_mean_change",
                "indicator_mean_relative_change",
            ]
        )
    except ValueError:
        ensemble_ds = ensemble_ds.drop_vars(
            [
                "indicator_stdev",
                "indicator_min",
                "indicator_max",
                "indicator",
            ]
        )

    ensemble_ds = ensemble_ds.rename_vars({"indicator_mean": "indicator"})
    ensemble_ds_stats = ensembles.ensemble_mean_std_max_min(ensemble_ds)
    ensemble_ds_percentiles = ensembles.ensemble_percentiles(
        ensemble_ds, split=False, values=[float(x) for x in config["ensembles"].values()]
    )

    ensemble_ds_result = xr.merge([ensemble_ds_stats, ensemble_ds_percentiles])
    ensemble_ds_result = ensemble_ds_result.assign(periodID=periods)
    ensemble_ds_result.to_netcdf(ensemble_filename)


def plot_and_save_spatial_plot(ensemble_change_filename: str, figure_filename: str):
    cmap = plt.cm.PuOr
    alpha = 0.8
    plot_limits = [-20, 20]
    ensemble_change_ds = xr.open_dataset(ensemble_change_filename)

    for period in [2, 3]:
        plt.figure()
        ensemble_change_ds["indicator_mean_relative_change"].sel(periodID=period).plot(
            robust=True, vmin=plot_limits[0], vmax=plot_limits[-1], cmap=cmap, alpha=alpha
        )
        plt.savefig(f"{figure_filename}_period_{period}.png")


def create_config(
    path_to_config: Path, path_to_periods: Path, scenario: str, indicator_id: str, units: str, indicator_name: str
) -> tuple[dict, str, str | None]:
    config = {}
    with open(path_to_config) as f:
        config["ensembles"] = yaml.safe_load(f)["ensembles"]

    config["periods"] = {}
    with open(path_to_periods) as f:
        periods_config = csv.reader(f, delimiter="\t")
        for line_no, line in enumerate(periods_config):
            if line_no == 0:
                keys = line
                continue

            if "#" in line[0]:
                continue

            config["periods"][f"{line_no}"] = {keys[idx]: line[idx] for idx in range(0, 4)}

    config["indicators"] = {indicator_id: {"units": units, "name": indicator_name}}
    config["scenarios"] = {
        "historical": {
            "id": "historical",
            "description": "Historical values",
            "scenarioStrings": ["_hist_"],
            "hexcolour": "66C2A5",
        }
    }

    CMIP5_scenarios = ["rcp26", "rcp45"]
    CMIP6_scenarios = ["ssp370"]
    if scenario in CMIP5_scenarios:
        CMIP_version = 5
        scenarios = CMIP5_scenarios
        config["scenarios"]["rcp26"] = {
            "id": "rcp26",
            "description": "Low emissions scenario (RCP2.6)",
            "scenarioStrings": ["_rcp26_"],
            "hexcolour": "FC8D62",
        }
        config["scenarios"]["rcp45"] = {
            "id": "rcp45",
            "description": "Medium emissions scenario (RCP4.5)",
            "scenarioStrings": ["_rcp45_"],
            "hexcolour": "8DA0CB",
        }
    elif scenario in CMIP6_scenarios:
        CMIP_version = 6
        scenarios = CMIP6_scenarios
        config["scenarios"]["ssp370"] = {
            "id": "ssp370",
            "description": "2nd worst scenario (SSP370)",
            "scenarioStrings": ["_ssp370_"],
            "hexcolour": "FC8D62",
        }
    else:
        CMIP_version = None

    return config, scenarios, CMIP_version


def create_csv(netcdf_statistics_filename: str, csv_filename: str):
    ds = xr.open_dataset(netcdf_statistics_filename)
    df_indicator_mean = ds.indicator.mean(dim=["Yc", "Xc"]).to_dataframe()
    df_indicator_mean.to_csv(csv_filename)


if __name__ == "__main__":
    current_dir = Path(__file__).parent
    scenario = "ssp370"
    indicator_id = "102"
    units = "kg m-2 s-1"
    indicator_name = "Annual mean precipitation by period"

    path_to_config = current_dir / "config/config_testcase_1.yaml"
    path_to_periods = current_dir / "config/periods_testcase_1.tsv"

    # Create config for this scenario/CMIP version, periods and indicator
    config, scenarios, CMIP_version = create_config(
        path_to_config, path_to_periods, scenario, indicator_id, units, indicator_name
    )

    # Note on csv filenames:
    # scenario has to be the third word, since makeBoxplot uses the third word in the filename
    # for mapping the scenarios in the legend
    path_to_save_netcdf = current_dir / f"testcase_1_results/model_ensembles/CMIP{CMIP_version}"
    statistics_filenames = [
        path_to_save_netcdf / f"{scenario}/{indicator_id}_{scenario}_ensemble_statistics.nc" for scenario in scenarios
    ]
    statistics_csv_filenames = [
        f"{path_to_save_netcdf}/{scenario}/{indicator_id}_ensemble_{scenario}_statistics.csv" for scenario in scenarios
    ]
    change_filenames = [
        path_to_save_netcdf / f"{scenario}/{indicator_id}_{scenario}_ensemble_change.nc" for scenario in scenarios
    ]
    historical_filename = path_to_save_netcdf / f"{indicator_id}_CMIP{CMIP_version}_historical_statistics.nc"
    historical_csv_filename = f"{path_to_save_netcdf}/{indicator_id}_CMIP{CMIP_version}_historical_statistics.csv"

    # Calculate ensemble statistics over models and save to netcdf
    if not historical_filename.exists():
        calculate_ensemble_mean(indicator_id, "historical", historical_filename, config, CMIP_version)

    for scenario, ensemble_statistics in zip(scenarios, statistics_filenames):
        if not ensemble_statistics.exists():
            calculate_ensemble_mean(indicator_id, scenario, ensemble_statistics, config)

    # Calculate ensemble change over models and save to netcdf
    for scenario, ensemble_change, ensemble_statistics in zip(scenarios, change_filenames, statistics_filenames):
        if not ensemble_change.exists():
            ensemble_stats_files = [str(ensemble_statistics), str(historical_filename)]
            netcdf_filename = [str(ensemble_change)]
            save_change_to_netcdf(config, indicator_id, scenario, ensemble_stats_files, netcdf_filename)

        # Plot spatial plot from ensemble change netcdf
        plot_and_save_spatial_plot(
            str(ensemble_change),
            f"{path_to_save_netcdf}/{scenario}/{indicator_id}_{scenario}_ensemble_mean_relative_change",
        )

    # Plot box plot from ensemble statistics netcdf
    csv_files_for_boxplot = [filename for filename in statistics_csv_filenames]
    csv_files_for_boxplot.append(historical_csv_filename)

    create_csv(historical_filename, historical_csv_filename)

    for scenario, ensemble_statistics, ensemble_csv in zip(scenarios, statistics_filenames, statistics_csv_filenames):
        ds_scenario = xr.open_dataset(ensemble_statistics)
        df_indicator_mean = ds_scenario.indicator.mean(dim=["Yc", "Xc"]).to_dataframe()
        df_indicator_mean.to_csv(ensemble_csv)

    makeBoxplot(
        config,
        indicator_id,
        csv_files_for_boxplot,
        [f"{path_to_save_netcdf}/{indicator_id}_CMIP{CMIP_version}_ensemble_boxplot.png"],
    )
