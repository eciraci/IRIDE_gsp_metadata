"""
Written by: Filippo Santarelli - February 2024

Utility functions to work with geospatial data.
 - Convert a file provided in csv, shp, parquet, and zip  to a GeoDataFrame.
"""
# - Python Dependencies:
from pathlib import Path
import logging
import zipfile
from typing import Optional, List
import fsspec
import geopandas as gpd
import pandas as pd


def read_dset_from_zip(zip_path: Path, **kwargs) -> gpd.GeoDataFrame:
    """
    Read a dataset from a ZIP file.
    Works only for zip files containing .csv and .zip files.
    Args:
        zip_path: absolute path to the ZIP file
        **kwargs:
    Returns:
        GeoDataFrame
    """
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zip_names = zipf.namelist()

    zip_path = Path(zip_path)
    if zip_path.with_suffix(".csv").name in zip_names:
        # - Changed to run on Windows systems
        with fsspec.open(f"zip://{zip_path.with_suffix(".csv").name}::"
                         + zip_path.as_posix()) as of:
            return read_csv_as_geodataframe(of, **kwargs)
    elif zip_path.with_suffix(".shp").name in zip_names:
        with fsspec.open("zip://*.shp::" + zip_path.as_posix()) as of:
            return read_as_geodataframe(of, **kwargs)
    elif zip_path.with_suffix(".parquet").name in zip_names:
        with (fsspec.open("zip://*.parquet::"
                          + zip_path.as_posix()) as of):
            return gpd.read_parquet(of)
    else:
        raise NotImplementedError("ZIP file must contain a CSV or SHP file")


def read_csv_as_geodataframe(path: Path, **kwargs) -> gpd.GeoDataFrame:
    """
    Read a CSV file as a GeoDataFrame
    :param path: absolute path to the file
    :param kwargs: dictionary of parameters passed to the read_csv method
    :return: gpd.GeoDataFrame
    """
    df = pd.read_csv(path, **kwargs)
    return gpd.GeoDataFrame(
        data=df,
        geometry=gpd.points_from_xy(df.easting, df.northing, crs=3035),
        crs=3035,
    )


def read_as_geodataframe(path: Path, **kwargs) -> Optional[gpd.GeoDataFrame]:
    """
    Read a file as a GeoDataFrame
    :param path: absolute path to the file
    :param kwargs: dictionary of parameters passed to the read_csv method
    :return: gpd.GeoDataFrame or None if file extension is not recognised

    Raises:
        NotImplementedError: for unsupported file format

    Note:
        The input ZIP, CSV, or parquet must have `easting` and `northing`
        fields; the input SHP must be in EPSG:4326.

    """
    path = Path(path)
    try:
        match path.suffix:
            case ".zip":
                return read_dset_from_zip(path, **kwargs)
            case ".csv":
                return read_csv_as_geodataframe(path, **kwargs)
            case ".shp":
                df = gpd.read_file(Path(path))
                return df
            case ".parquet":
                df = gpd.read_parquet(Path(path))
                return df
            case _:
                logging.error(f"File extension {path.suffix} not recognised")
                return None
    except Exception as e:
        logging.error(f"Error reading file {path}: {e}")
        return None
