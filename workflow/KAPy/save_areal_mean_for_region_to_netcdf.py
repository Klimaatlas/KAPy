import xarray as xr
import geopandas as gpd
import matplotlib.pyplot as plt
from osgeo import gdal
import rasterio
from shapely.geometry import mapping

def save_areal_mean_for_region_to_netcdf(config: dict, indicator_id: str, scenario: str, period: str, region: str, inputs: list[str], output: str):
    """
    Saves mean and percentiles of indicator for one scenario, period and region as netcdf.

    Args:
        config: configuration from KAPy that contains information from all configuration files
        indicator_id: which parameter in the input file to calculate ensemble statistics for
        scenario: ssp370 for CMIP6 and rcp26 and rcp45 for CMIP5 inputs
        period: near future or far future
        region: id for region in shapefile defined in configuration file to cut out of input file and calculate ensemble statistics for
        inputs: original datasets with 30 year means
        output: path to output directory including netcdf file name
    
    Returns:
        Nothing, but saves the areal mean and percentiles to netcdf for the input scenario, period and region, as well as a spatial plot
    """
    indicator_name = config["indicators"][indicator_id]["variables"]
    region_datasets = {}
    polygons_file = gpd.read_file(config["region"][region]["shapefile"])
    polygon = gpd.GeoSeries(data=polygons_file.iloc[int(region)].geometry, crs=polygons_file.crs)

    for input_file in inputs:
        dataset = xr.open_dataset(input_file)
        projection = gdal.Open(input_file).GetProjection()
        dataset = dataset.rio.write_crs(projection)
        polygon = polygon.to_crs(projection)
        
        mask = rasterio.features.geometry_mask([mapping(polygon.geometry[0])], out_shape=(len(dataset.Yc), len(dataset.Xc)), transform=dataset.rio.transform(), invert=True)
        # all_touched=False by default, means "If False, only pixels whose center is within the polygon or that are selected by Bresenham’s line algorithm will be burned in"
        mask= xr.DataArray(mask, dims=("Yc", "Xc"))
        clipped_ds = dataset.where(mask, drop=True)
        region_datasets[input_file] = clipped_ds

    datasets = [region_datasets[filename] for filename in region_datasets if period in filename]
    dataset_total = xr.combine_nested(datasets, concat_dim="realization")

    # Take mean over all bias adjustments
    dataset_mean = dataset_total[indicator_name].mean(dim=["realization"])

    # Take areal mean
    dataarray_areal_mean = dataset_mean.mean(dim=["Yc", "Xc"])
    dataarray_areal_mean = dataarray_areal_mean.rename("indicator_mean")
    dataarray_areal_mean = dataarray_areal_mean.rename({"time": "periodID"})
    dataarray_areal_mean.to_netcdf(output)

    limit = [-15, 15]
    plt.figure()
    dataset_mean.plot(robust=True, vmin=limit[0], vmax=limit[-1])
    plt.savefig(f"{output.split(indicator_id)[0]}/{indicator_id}_{scenario}_{period}_region_{region}_pr_mean.png")

    # plt.figure()
    # dataset_total.sel(Xc=list(np.arange(195500, 205500, 1000))).sel(Yc=list(np.arange(6889500, 6840500, -1000))).plot.scatter(x="Xc", y="Yc", hue=indicator_name, cmap="viridis")
    # plt.savefig(f"{output.split(indicator_id)[0]}/{indicator_id}_{scenario}_{period}_region_{region}_test.png")

 