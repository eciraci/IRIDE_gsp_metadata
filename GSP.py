"""
Written by Enrico Ciracì - April 2024


Python Dependencies:
geopandas: Open source project to make working with geospatial data
    in python easier: https://geopandas.org
rasterio: Python library to read and write geospatial raster data:
    https://rasterio.readthedocs.io/en/latest/
"""
# - Python Dependencies:
import dataclasses
from abc import ABC, abstractmethod
import geopandas as gpd
from pathlib import Path
from typing import Tuple, Any
import rasterio
from rasterio.io import MemoryFile
from rasterio.warp import calculate_default_transform, reproject, Resampling
# - Local Dependencies:
from read_as_geodataframe import read_as_geodataframe


class AbstractGSP(ABC):
    """
    Abstract base class for handling Geospatial Products (GSP).
    """

    @abstractmethod
    def load_gsp(self, gsp_path: str):
        """Load a Geospatial Product (GSP) file."""
        pass

    @abstractmethod
    def get_bbox(self) -> list:
        """Return the bounding box of the GSP file."""
        pass

    @abstractmethod
    def get_crs(self) -> str:
        """Return the coordinate reference system of the GSP file."""
        pass

    @abstractmethod
    def set_crs(self, new_crs: str) -> None:
        """Set the coordinate reference system of the GSP file."""
        pass

    @abstractmethod
    def get_envelope(self) -> Any:
        """Return the envelope of the GSP file."""
        pass


@dataclasses.dataclass
class VectorGSP(AbstractGSP):
    """
    Class to handle Geospatial Products (GSP) files.
    """
    gdf: gpd.GeoDataFrame = dataclasses.field(default=None, init=False)
    epsg: int = dataclasses.field(default=4326, init=False)

    def load_gsp(self, gsp_path: str | Path) -> None:
        """Import a Geospatial Product (GSP) file."""
        self.gdf = read_as_geodataframe(gsp_path)

    def get_bbox(self) -> Tuple[float, float, float, float]:
        """Return the bounding box of the GSP file."""
        return self.gdf.total_bounds

    def get_crs(self) -> str:
        """Return the coordinate reference system of the GSP file."""
        return self.gdf.crs

    def set_crs(self, new_crs: str) -> None:
        """Set the coordinate reference system of the GSP file."""
        self.gdf = self.gdf.to_crs(new_crs)

    def get_envelope(self) -> Any:
        """Return the envelope of the GSP file."""
        xmin, ymin, xmax, ymax = self.get_bbox()
        envelope = [(xmin, ymin), (xmin, ymax), (xmax, ymax),
                    (xmax, ymin), (xmin, ymin)]
        return envelope


@dataclasses.dataclass
class RasterGSP(AbstractGSP):
    """
    Class to handle Geospatial Products (GSP) files in raster format.
    """
    raster: Any = dataclasses.field(default=None, init=False)

    def load_gsp(self, gsp_path: str | Path) -> None:
        """Import a Geospatial Product (GSP) file in raster format."""
        self.raster = rasterio.open(gsp_path)

    def get_bbox(self) -> list:
        """Return the bounding box of the GSP file."""
        return list(self.raster.bounds)

    def get_crs(self) -> str:
        """Return the coordinate reference system of the GSP file."""
        return self.raster.crs.to_string()

    def set_crs(self, new_crs: str) -> rasterio.io.DatasetReader:
        """Change the CRS of the raster data and return the new dataset."""
        new_crs = rasterio.crs.CRS.from_string(new_crs)
        transform, width, height = calculate_default_transform(
            self.raster.crs, new_crs, self.raster.width, self.raster.height,
            *self.raster.bounds)
        kwargs = self.raster.meta.copy()
        kwargs.update({
            'crs': new_crs,
            'transform': transform,
            'width': width,
            'height': height
        })

        with MemoryFile() as memfile:
            with memfile.open(**kwargs) as dst:
                for i in range(1, self.raster.count + 1):
                    reproject(
                        source=rasterio.band(self.raster, i),
                        destination=rasterio.band(dst, i),
                        src_transform=self.raster.transform,
                        src_crs=self.raster.crs,
                        dst_transform=transform,
                        dst_crs=new_crs,
                        resampling=Resampling.nearest)
            return memfile.open()

    def get_envelope(self) -> Any:
        """Return the envelope of the GSP file."""
        xmin, ymin, xmax, ymax = self.get_bbox()
        envelope = [(xmin, ymin), (xmin, ymax), (xmax, ymax),
                    (xmax, ymin), (xmin, ymin)]
        return envelope
