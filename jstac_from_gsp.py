#!/usr/bin/env python
u"""
Written by:  Enrico Ciraci' - February 2024

Add a JSON STAC file to an existing Geospatial Products (GSP) file
saved inside a .zip archive.

Python Dependencies:
geopandas: Open source project to make working with geospatial data
    in python easier: https://geopandas.org
dask_geopandas: Dask-based parallelized geospatial operations
    for GeoPandas: https://dask-geopandas.readthedocs.io/en/stable/
pystac: Python library for working with SpatioTemporal Asset Catalogs
    (STAC): https://pystac.readthedocs.io/en/latest/
"""
# - Python Dependencies
import os
from datetime import datetime, timezone, UTC
import zipfile
from pathlib import Path
import dataclasses
from typing import Tuple
# - Third-Party Dependencies
import pystac
import geopandas as gpd
from pystac.extensions.sar import SarExtension, FrequencyBand, Polarization
from pystac.extensions.sat import SatExtension, OrbitState
from pystac.extensions.projection import ProjectionExtension

from xml_utils import extract_xml_from_zip
from iride_utils.aoi_info import get_aoi_info
from iride_utils.collection_info import collection_info
from iride_utils.gsp_description import gsp_description

# - Set Processing Time as a constant
# - For the first IRIDE data release, set this value equal to
# - the 15th on March 2024 at 00:00:00 UTC
PROC_TIME = proc_datetime = datetime(2024, 3, 15, 0, 0, 0, 0, timezone.utc)


def update_zip(zip_name: str, file_name: str) -> None:
    """
    Update a file inside a zip archive
    :param zip_name: absolute path to the zip file
    :param file_name: absolute path to the file to be added
    :return: None
    """
    # - generate a temporary copy of the input zip file
    temp_zip = zip_name.replace('.zip', '_temp.zip')

    # - read zip archive content
    with zipfile.ZipFile(zip_name, 'r') as zin:
        with zipfile.ZipFile(temp_zip, 'w') as zout:
            zout.comment = zin.comment      # - preserve zip comment
            for item in zin.infolist():
                if item.filename != os.path.basename(file_name):
                    # - Copy all other files to the new archive
                    zout.writestr(item.filename, zin.read(item.filename))
    # - Replace original archive with the temp archive
    os.remove(zip_name)
    os.rename(temp_zip, zip_name)

    # Add the new file with its new data
    with zipfile.ZipFile(zip_name, mode='a',
                         compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(file_name, os.path.basename(file_name))


@dataclasses.dataclass
class GSP:
    gdf: gpd.GeoDataFrame = dataclasses.field(default=None, init=False)
    epsg: int = dataclasses.field(default=4326, init=False)

    def load_gsp(self, gsp_path: str | Path, epsg: int = 4326) -> None:
        self.gdf = gpd.read_file(gsp_path).to_crs(epsg=epsg)

    def get_bounds(self) -> Tuple[float, float, float, float]:
        return self.gdf.total_bounds

    def get_envelope(self) -> Tuple[float]:
        return self.gdf.unary_union.envelope.exterior.coords.xy


def main() -> None:
    # - Set Parameters
    overwrite = True                # - overwrite existing files
    validate_schema = True          # - validate STAC schema
    print_info = True               # - print information
    epsg = 4326                     # - EPSG code for the GSP file
    collection_id = "ISS_S304SNT02"
    gsp_ext = "shp"       # - extension of the GSP file

    # - Path to sample GSP
    data_dir = os.path.join(os.path.expanduser('~'), 'Desktop',
                            'Scripts', 'lot2')
    # - GSP file name - equivalent to product_id in the XML metadata file
    item_id = 'ISS_S304SNT03_20180701_20230623_044BRNA_01'

    zip_path = os.path.join(data_dir,  f'{item_id}.zip')
    gsp_path = os.path.join(data_dir, f'{item_id}.zip!{item_id}.{gsp_ext}')

    print(f"# - GSP Path: {gsp_path}")
    print('# - Loading GSP...')

    # - Load GSP
    s_time = datetime.now()
    gdf_smp = GSP()
    gdf_smp.load_gsp(gsp_path, epsg=epsg)

    # - Convert To GeoPandas DataFrame
    xmin, ymin, xmax, ymax = gdf_smp.get_bounds()
    # - Set Bounding Box
    bbox = [xmin, ymin, xmax, ymax]

    # - Extract dataset envelope polygon
    envelope = gdf_smp.get_envelope()
    xs = list(envelope[0])
    ys = list(envelope[1])
    crd = list(zip(xs, ys))
    # - Express GPS envelope as a GeoJSON geometry
    env_geometry = {
        "type": "Polygon",
        "coordinates": [crd],
    }

    # - Compute datasets loading time
    e_time = datetime.now()
    print(f"# - Dataframe Loading  Time: {e_time - s_time}")

    # - Read XML Metadata
    meta_dict = extract_xml_from_zip(zip_path)[0]
    gsp_id = meta_dict['gsp_id']    # - GPS ID [TD3 ID]
    product_id = meta_dict['product_id']        # - Product ID [File Name]
    aoi = get_aoi_info(meta_dict['aoi'])['aoi_name']   # - Area of Interest
    collection_title = gsp_description(gsp_id)      # - Collection Title
    # - Geospatial Product Short Description
    collection_s_descr = collection_title
    # - Derive Dataset Collection from GSP ID
    collection_description = collection_info(gsp_id)

    # - Extract Start and End Dates and convert the into datetime objects
    # - Note: dates from the XML metadata are in the format: YYYYMMDD
    # -       convert them to YYYY-MM-ddT00:00:00Z format.
    s_yyyy = meta_dict['start_date'][:4]
    s_mm = meta_dict['start_date'][4:6]
    s_dd = meta_dict['start_date'][6:]
    start_date \
        = datetime.strptime(f"{s_yyyy}-{s_mm}-{s_dd}T00:00:00Z",
                            '%Y-%m-%dT00:00:00Z')
    e_yyyy = meta_dict['end_date'][:4]
    e_mm = meta_dict['end_date'][4:6]
    e_dd = meta_dict['end_date'][6:]
    end_date \
        = datetime.strptime(f"{e_yyyy}-{e_mm}-{e_dd}T00:00:00Z",
                            '%Y-%m-%dT00:00:00Z')
    time_interval = [start_date, end_date]  # - Dataset Time Interval

    # - Create STAC Item - #
    # - Define PyStac SpatioTemporal Extent
    extent = pystac.Extent(
        spatial=pystac.SpatialExtent(bbox),
        temporal=pystac.TemporalExtent([time_interval]),
    )

    # - Define Activation Collection
    activation_collection = pystac.Collection(
        id=collection_id,
        description=collection_description,
        title=collection_title,
        extent=extent
    )

    #  - Validate activation collection format
    print("# - Validate Activation Collection:")
    print(pystac.validation.validate(activation_collection))

    # - Write Activation Collection to JSON file
    pystac.write_file(
        obj=activation_collection,
        include_self_link=False,
        dest_href=os.path.join(data_dir, "collection.json")
    )

    # - Create STAC Item
    item = pystac.Item(
        id=item_id,
        geometry=env_geometry,
        bbox=bbox,
        properties={},
        datetime=proc_datetime,
        stac_extensions=[],
        collection=collection_id,
    )

    # - Add GSP Assets to STAC Item
    item.add_asset(
        "GSP",
        asset=pystac.Asset(
            href=f"./{item_id}.{gsp_ext}",
            media_type="application/{gsp_ext}",
            title=f"Lot 2 Geospatial Product: {item.id}",
            description=collection_s_descr,
            roles=["data", "visual"],
        ),
    )

    # -  Add GSP Metadata Asset
    item.add_asset(
        "GSP-Metadata",
        asset=pystac.Asset(
            href=f"./{item_id}.xml",
            media_type="application/xml",
            title=f"ISO-19115 metadata for {item.id}",
            description=f"ISO-19115 metadata for {item.id}",
            roles=["metadata", "iso-19115"],
        ),
    )

    # - Add STAC Extensions
    proj_ext = ProjectionExtension.ext(item, add_if_missing=True)
    sar_ext = SarExtension.ext(item, add_if_missing=True)
    sat_ext = SatExtension.ext(item, add_if_missing=True)

    #TODO: updated these lines
    item.properties["gsp_id"] = gsp_id
    item.properties["product_id"] = product_id
    item.properties["description"] = collection_s_descr
    item.properties["AOI"] = aoi
    item.properties["start_datetime"] \
        = start_date.replace(tzinfo=timezone.utc).isoformat()
    item.properties["end_datetime"] \
        = end_date.replace(tzinfo=timezone.utc).isoformat()
    item.properties["constellation"] = "Sentinel-1"
    item.properties["platform"] = "Sentinel-1A"
    item.properties["license"] = "TBD"
    item.properties["proj:epsg"] = 4326
    item.properties["sat:orbit_state"] = "descending"
    item.properties["sar:frequency_band"] = FrequencyBand("C")
    item.properties["sar:polarizations"] \
        = [Polarization("VV"), Polarization("VH")]
    item.properties["sar:instrument_mode"] = "IW"
    item.properties["sar:product_type"] = "SLC"
    item.properties["providers"] = [{"name": "eGeos",
                                     "roles": ["producer", "processor"],
                                     "url": "https://www.e-geos.it/"}
                                    ]

    # - Add Link to Collection
    item.add_link(link=pystac.Link(rel="collection",
                                   target="collection.json"))

    # - Validate Item
    if validate_schema:
        #  - Validate activation collection format
        print("# - Validate Activation Collection:")
        print(pystac.validation.validate(activation_collection))
        print(f"# - Validate Item: {item.id}")
        item.validate()

    # - Convert Item to Dictionary
    if print_info:
        item.to_dict()

    # - Write Item to JSON file
    pystac.write_file(obj=item, include_self_link=False,
                      dest_href=os.path.join(data_dir, f"{item_id}.json"))

    with zipfile.ZipFile(os.path.join(data_dir, f'{item_id}.zip'),
                         'r') as zipf:
        zip_names = zipf.namelist()

    # - Add JSON STAC file to the zip archive
    if (f"{item_id}.json" in zip_names and overwrite)\
            or (f"{item_id}.json" not in zip_names):
        # - Update the zip archive
        # - Item JSON file
        update_zip(os.path.join(data_dir,  f'{item_id}.zip'),
                   os.path.join(data_dir, f"{item_id}.json"))
        # - Collection JSON file
        update_zip(os.path.join(data_dir,  f'{item_id}.zip'),
                   os.path.join(data_dir, "collection.json"))

    # - Remove temporary JSON files
    # os.remove(os.path.join(data_dir, f"{item_id}.json"))
    # os.remove(os.path.join(data_dir, "collection.json"))


# - run main program
if __name__ == '__main__':
    start_time = datetime.now()
    main()
    end_time = datetime.now()
    print(f"# - Computation Time: {end_time - start_time}")
