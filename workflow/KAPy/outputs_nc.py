import os
import xarray as xr
import pickle
from pathlib import Path
import shutil

# Use absolute imports assuming KAPy is installed
from KAPy import helpers

def _write_dataarray(da: xr.DataArray, var_name: str, output_path: str):
    # Choose output format
    format = os.path.splitext(os.path.basename(output_path))[1]
    if format == ".nc":
        da.name = var_name
        chunkThisWay = helpers.align_chunking(da)
        da.to_netcdf(
            output_path,
            encoding={
                var_name: {"chunksizes": chunkThisWay, "zlib": True, "complevel": 1}
            },
        )
    elif format == ".pkl":  # Write as pickle
        with open(output_path, "wb") as f:
            pickle.dump(da, f)
    else:
        raise IOError(
            f"Unknown file format, '{format}' inferred from: '{output_path}'."
        )



def write_variables(
    obj: xr.DataArray | xr.Dataset | dict[str,str], path: dict[str, str]
) -> None:
    """
    Write variables as xarray objects to disk as NetCDF files.

    Parameters
    ----------
    obj : xr.DataArray, xr.Dataset, dict
        The data to write, either as a single DataArray, a dataset or a dict of paths to files.
    path : dict
        Mapping of variable names to output file paths.
        For a single DataArray, should have one key matching the variable name.
        For a Dataset, keys should match dataset variables.
    """

    if isinstance(obj, xr.DataArray):
        # Expect exactly one key in path
        if len(path) != 1:
            raise ValueError(
                f"Expected exactly one path for a single DataArray: received {path}"
            )
        _write_dataarray(
            obj, var_name=next(iter(path.keys())), output_path=next(iter(path.values()))
        )

    elif isinstance(obj, xr.Dataset):
        #Check that the keys in path can be found in the xr.Dataset obj
        for this_key in path.keys():
            if not (this_key  in obj):  
                raise ValueError(
                    f"Cannot find variable {this_key} in xarray dataset."
                )
            _write_dataarray(
                obj[this_key], var_name=this_key, output_path=path[this_key]
            )

    elif isinstance(obj, dict):
        # Accept instances where the object is a dict of paths to a file.
        # There should be agreement between the keys in the path and obj file.
        # Check this first
        if not obj.keys() == path.keys():
            raise ValueError(
                f"Mismatch between variables expected and returned by the function. Expected: {list(path.keys())}. Returned: {list(obj.keys())}"
            )
        # Loop over the dicts. If the path contained in the object matches the desired output path,
        # then the result should already be in the right place. Else move the file in  obj to the output path
        for this_key in path.keys():
            if obj[this_key] != path[this_key]:
                shutil.move(Path(obj[this_key]), Path(path[this_key]))

    else:
        raise TypeError(f"Unsupported type: {type(obj)}")


def write_indicators(obj: xr.Dataset | dict, path: dict[str, str]) -> None:
    """
    Write indicators to disk as NetCDF files.

    Parameters
    ----------
    obj :  xr.Dataset | dict
        The data to write, provided either as a dataset or a dict. If a dict multiple files are written.
    path : dict
        Mapping of indicator names to output file paths.
    """

    if isinstance(obj, xr.Dataset):
        # Expect exactly one key in path
        if len(path) != 1:
            raise ValueError("Expected exactly one path for a single dataset")
        if isinstance(path, dict):
            path = list(path.values())
        obj.to_netcdf(path[0])

    elif isinstance(obj, dict):
        for ind in path.keys():
            if ind not in obj:
                raise KeyError(
                    f"Cannot find indicator '{ind}' in provided dict to write with keys {obj.keys()}"
                )
            dat = obj[ind]
            dat.to_netcdf(path[ind])

    else:
        raise TypeError(f"Unsupported type: {type(obj)}")
