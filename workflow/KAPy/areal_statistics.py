import xarray as xr
import pandas as pd
import geopandas as gpd
from cdo import Cdo
import regionmask
from pathlib import Path


def _check_geojson(gdf, filename):
    if Path(filename).suffix.lower() not in {".geojson", ".json"}:
        return

    if gdf.crs is None:
        raise ValueError("GeoJSON requires a CRS, but the GeoDataFrame has no CRS.")

    epsg = gdf.crs.to_epsg()
    if epsg != 4326:
        raise ValueError(
            f"Attempting to use GeoJSON with CRS {gdf.crs!r}. "
            "GeoJSON should be written in EPSG:4326 (lon-lat)."
        )

    minx, miny, maxx, maxy = gdf.total_bounds
    if minx < -180 or maxx > 180 or miny < -90 or maxy > 90:
        raise ValueError(
            "CRS claims to be EPSG:4326, but the coordinate values do not "
            f"look like longitude/latitude: x-range {[minx,maxx]}, y-range {[miny,maxy]}."
        )


def generate_areal_statistics(inFile, tempDir, useAreaWeighting, shapefile):
    """
    Generate statistics over an area by applying a polygon mask and averaging

    Parameters
    ----------
    inFile : _type_
        _description_
    tempDir : _type_
        _description_
    useAreaWeighting : _type_
        _description_
    shapefile : _type_
        _description_

    Returns
    -------
    _type_
        _description_

    Raises
    ------
    ValueError
        _description_
    ImportError
        _description_
    """

    # Setup xarray
    # Note that we need to use open_dataset here, as the ensemble files have
    # multiple data variables in them
    time_coder = xr.coders.CFDatetimeCoder(use_cftime=True)
    thisDat = xr.open_dataset(inFile, decode_times=time_coder, decode_timedelta=False)

    # Replace time with a period code generated from time_bnds following ISO8601
    time_period_codes = [
        f"{x[0]:%Y-%m-%d}/{x[1]:%Y-%m-%d}" for x in thisDat["time_bnds"].values
    ]
    thisDat = thisDat.assign_coords(time=("time", time_period_codes))

    # Then drop time_bnds and season_mask
    thisDat = thisDat.drop_vars(["time_bnds", "season_mask"])

    # Identify coordinate types. Some logic is required here, as the coordinates
    # presented can vary based whether it is an ensemble stat or member
    spDims = list(
        set(thisDat.dims) - set(["time", "season", "percentiles", "nv", "month"])
    )
    nonspDims = list(set(thisDat.dims) - set(spDims))
    spGrid = thisDat.isel({k: 0 for k in nonspDims}, drop=True)[
        list(thisDat.data_vars)[0]
    ]

    # If using area weighting, get the pixel size
    if useAreaWeighting:
        cdo = Cdo(tempdir=tempDir)
        pxlSize = cdo.gridarea(input=spGrid, returnXArray="cell_area")
    else:
        pxlSize = spGrid
        pxlSize.values[:] = 1
        pxlSize.name = "cell_area"

    # If we have a shapefile defined, then work with it
    if shapefile is not None:
        # Import shapefile
        # Reset the index to be 0..N so that we avoid any potential auto-indexing from geopandas
        shpFile = gpd.read_file(shapefile)
        shpFile = shpFile.reset_index(drop=True)

        # If the shapefile is missing a CRS, stop - we don't want to assume anything here
        if shpFile.crs is None:
            raise ImportError(
                f"Shapefile '{shapefile}' is lacking a CRS (Coordinate Reference System) "
                + "but this is required for KAPy to work. Please add a CRS in the shapefile."
            )

        # GeoJSONs are supported, but require extra checks
        _check_geojson(shpFile, shapefile)

        # Handle projection issues.
        # 1. If the file has supplementary coordinates of longitude and latitude, then reproject
        #    the shapefile to long-lat and use together with the supplementary coordinates
        if bool(set(["lat", "latitude"]) & set(thisDat.coords)) & bool(
            set(["lon", "longitude"]) & set(thisDat.coords)
        ):
            shpFile = shpFile.to_crs("EPSG:4326")  # Lon-lat
            xDim = spGrid["lon" if "lon" in list(spGrid.coords) else "longitude"]
            yDim = spGrid["lat" if "lat" in list(spGrid.coords) else "latitude"]
            useSupCoords = True

        # 2. Otherwise assert that the user has checked that the two CRS match.
        #    Ideally we should check this, but I'm not convinced that it can be done robustly.
        else:
            useSupCoords = False

        # Loop over polygons
        outList = []
        for thisIdx, thisArea in shpFile.iterrows():
            # Which points are in the polygon? Setup a mask
            if useSupCoords:
                pxlMask = regionmask.mask_geopandas(shpFile.iloc[[thisIdx]], xDim, yDim)
            else:
                pxlMask = regionmask.mask_geopandas(shpFile.iloc[[thisIdx]], spGrid)
            pxlWts = xr.where(~pxlMask.isnull(), pxlSize, 0)

            # Apply masking and weighting and calculate
            wtMeanDf = (
                thisDat.weighted(pxlWts).mean(dim=spDims).to_dataframe().reset_index()
            )
            wtMeanDf["statisticType"] = "mean"
            wtSdDf = (
                thisDat.weighted(pxlWts).std(dim=spDims).to_dataframe().reset_index()
            )
            wtSdDf["statisticType"] = "sd"

            # Output object
            thisOut = pd.concat([wtMeanDf, wtSdDf])
            thisOut.insert(0, "areaID", thisIdx)
            outList += [thisOut]
        dfOut = pd.concat(outList)

    # Otherwise, just average spatially
    else:
        # Average spatially over the time dimension
        spMean = thisDat.weighted(pxlSize).mean(dim=spDims)
        spMeanDf = spMean.to_dataframe()
        spMeanDf["statisticType"] = "mean"
        spSd = thisDat.weighted(pxlSize).std(dim=spDims)
        spSdDf = spSd.to_dataframe()
        spSdDf["statisticType"] = "sd"

        # Save files pandas. Set the areaID to NA
        dfOut = pd.concat([spMeanDf, spSdDf])
        dfOut.insert(0, "areaID", "NA")
        dfOut = dfOut.reset_index()

    # Return dfOut. Writing is handled by the calling function
    return dfOut


# Development configuration----------------------------
if __name__ == "__main__":
    # Setup for debugging
    # ASSERT: working directory is the root of the project
    import KAPy

    config = KAPy.get_config("./config/config.yaml")
    wf = KAPy.get_workflow(config)
    output_file = list(wf["areal_statistics"]["input_dict"].keys())[0]
    inFile = wf["areal_statistics"]["input_dict"][output_file][0]
    print(f"Using input file: {inFile}")
    print(f"based on requirements for output file: {output_file}")

    # Set options
    import tempfile

    tempDir = tempfile.gettempdir()

    # Run without a shapefile
    print("Running without a shapefile------------------")
    useAreaWeighting = True
    shapefile = None
    without_shp = generate_areal_statistics(
        inFile, tempDir, useAreaWeighting, shapefile
    )
    print("Success!")

    # Run with a shapefile
    print("Running with a shapefile------------------")
    shapefile = "docs/tutorials/Tutorial05_files/Ghana_regions.shp"
    useAreaWeighting = True
    with_shp = generate_areal_statistics(inFile, tempDir, useAreaWeighting, shapefile)
    print("Success!")
