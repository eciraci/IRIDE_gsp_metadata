#!/usr/bin/env python
u"""
Written by:  Enrico Ciraci' - February 2024

Add a JSON STAC file to an existing Geospatial Products (GSP) file
saved inside a .zip archive.
The archive may contain a Geospatial Product (GSP) file in one of the
following formats: 'shp', 'csv', 'geojson', 'gpkg', 'parquet', 'tif'.
An associated XML metadata file is also expected to be present in the
archive.

usage: jstac_from_gsp.py [-h] [-O] [-V] [-P] [-E EPSG]
    [-G {shp,csv,geojson,gpkg,parquet,tif,tiff}] gsp_path

Add a JSON STAC file to an existing Geospatial Products (GSP)
file saved inside a .zip archive.

positional arguments:
  gsp_path              Path to the Geospatial Product (GSP) file.

options:
  -h, --help            show this help message and exit
  -O, --overwrite       Overwrite existing files.
  -V, --validate_schema
                        Validate STAC schema.
  -P, --print_info      Print generated JSON STAC to std output.
  -E EPSG, --epsg EPSG  EPSG code for the GSP file.
  -G {shp,csv,geojson,gpkg,parquet,tif,tiff}, --gsp_ext {shp,csv,geojson,
        gpkg,parquet,tif,tiff} Geospatial Product Extension.


Python Dependencies:
geopandas: Open source project to make working with geospatial data
    in python easier: https://geopandas.org
pystac: Python library for working with SpatioTemporal Asset Catalogs
    (STAC): https://pystac.readthedocs.io/en/latest/
shapely: Python package for manipulation and analysis of planar geometric
    objects: https://pypi.org/project/Shapely/
fiona: Fiona is OGR's neat, nimble, no-nonsense API for Python
    programmers: https://pypi.org/project/Fiona/
pyproj: Python interface to PROJ (cartographic projections and
    coordinate transformations library): https://pypi.org/project/pyproj/
xmltodict: Python module that makes working with XML feel like you are
    working with JSON: https://pypi.org/project/xmltodict/
lxml: Pythonic binding for the C libraries libxml2 and libxslt:
    https://pypi.org/project/lxml/
"""
# - Python Dependencies
import os
import argparse
from datetime import datetime, timezone
import zipfile
import tempfile
from pathlib import Path
from typing import Tuple, Dict, Any
# - Third-Party Dependencies
import pystac
from pystac.extensions.sar import SarExtension, FrequencyBand, Polarization
from pystac.extensions.sat import SatExtension, OrbitState
from pystac.extensions.projection import ProjectionExtension
# - Local Dependencies
from xml_utils import extract_xml_from_zip
from iride_utils.aoi_info import get_aoi_info
from iride_utils.collection_info import collection_info
from iride_utils.gsp_description import gsp_description
from GSP import VectorGSP, RasterGSP

# - Set Processing Time as a constant
# - For the first IRIDE data release, set this value equal to
# - the 15th on March 2024 at 00:00:00 UTC
PROC_TIME = proc_datetime = datetime(2024, 3, 15, 0, 0, 0, 0, timezone.utc)


class ZipHandler:
    """
    Class to handle zip archives.
    """
    @staticmethod
    def update_zip(zip_name: str, file_name: str) -> None:
        """
        Update a file inside a zip archive
        :param zip_name: absolute path to the zip file
        :param file_name: absolute path to the file to be addedSS
        :return: None
        """
        # - Generate temporary file name
        tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(zip_name))
        os.close(tmpfd)

        # - create a temp copy of the archive without filename
        with zipfile.ZipFile(zip_name, 'r') as z_in:
            with zipfile.ZipFile(tmpname, 'w') as z_out:
                z_out.comment = z_in.comment     # - preserve the comment
                for item in z_in.infolist():
                    if item.filename != os.path.basename(file_name):
                        # - Copy all other files to the new archive
                        z_out.writestr(item, z_in.read(item.filename))
        # - Replace the temporary archive with the original
        os.remove(zip_name)
        os.rename(tmpname, zip_name)

        # - Add the new file with its new data
        with zipfile.ZipFile(zip_name, mode='a',
                             compression=zipfile.ZIP_DEFLATED) as zf:
            zf.write(file_name, os.path.basename(file_name))

    @staticmethod
    def check_file_in_zip(zip_path: str, file_format: str) -> bool:
        """
        Check if a zip archive contains a file saved in a specified format.
        :param zip_path: Path to the zip file.
        :param file_format: The file format to check for.
        :return: True if a file of the specified format is found,
            False otherwise.
        """
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            for file in zipf.namelist():
                if file.endswith(file_format):
                    return True
        return False


def return_sensor_info(sensor_tag: str) -> Dict[str, Any]:
    """
    Return the Satellite Constellation and Sensor Information give a
    predefined sensor tag.
    :param sensor_tag: mission tag
    :return: Python Dictionary containing sensor information
    """
    if sensor_tag in ['SNT', "S1A", "S1B"]:
        if sensor_tag == "S1A":
            const = "Sentinel-1"
            sensor = "Sentinel-1A"

        elif sensor_tag == "S1B":
            const = "Sentinel-1"
            sensor = "Sentinel-1B"

        else:
            const = "Sentinel-1"
            sensor = "Sentinel-1"
        band = "C"
        polarization = ["HH", "HV"]

    elif sensor_tag in ["CSM", "CSK", "CSG"]:
        if sensor_tag == "CSG":
            const = "COSMO-SkyMed"
            sensor = "COSMO-SkyMed Sec-Gen"
        else:
            const = "COSMO-SkyMed"
            sensor = "COSMO-SkyMed"
        band = "X"
        polarization = ["HH", "HV"]

    elif sensor_tag in ["SAO"]:
        const = "SAOCOM"
        sensor = "SAOCOM"
        band = "L"
        polarization = ["HH", "HV"]
    else:
        raise ValueError(f"Unknown sensor tag: {sensor_tag}")

    return {"constellation": const, "sensor": sensor,
            "band": band, "polarization": polarization}


def split_date(date: str) -> Tuple[str, str, str]:
    """
    Split the date string into year, month, and day
    :param date: date string in the format YYYYMMDD
    :return: Tuple of strings (year, month, day)
    """
    # - Check if the date is in the format: DD/MM/YYYY
    if '/' in date:
        s_date = date.split('/')
        s_yyyy = s_date[2]
        s_mm = s_date[1]
        s_dd = s_date[0]
    else:
        s_yyyy = date[:4]
        s_mm = date[4:6]
        s_dd = date[6:]

    return s_yyyy, s_mm, s_dd


def main() -> None:
    """Main program."""
    # - Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Add a JSON STAC file to an existing Geospatial Products "
                    "(GSP) file saved inside a .zip archive."
    )
    # - GSP file path
    parser.add_argument('gsp_path', type=str,
                        help='Path to the Geospatial Product (GSP) file.')
    # - Overwrite existing files
    parser.add_argument('-O', '--overwrite', action='store_true',
                        help='Overwrite existing files.')
    # - Validate STAC schema
    parser.add_argument('-V', '--validate_schema',
                        action='store_true',  help='Validate STAC schema.')
    # - Print information
    parser.add_argument('-P', '--print_info',
                        action='store_true',
                        help='Print generated JSON STAC to std output.')
    # - EPSG code for the GSP file
    parser.add_argument('-E', '--epsg', type=int, default=4326,
                        help='EPSG code for the GSP file.')
    # - Geospatial Product Extension
    # - By default, the GSP file extension is set to 'shp'
    parser.add_argument('-G', '--gsp_ext', type=str,
                        default='shp', help='Geospatial Product Extension.',
                        choices=['shp', 'csv', 'tif', 'tiff'])
    # - Parse the arguments
    args = parser.parse_args()

    # - Set Parameters
    overwrite = args.overwrite      # - overwrite existing files
    validate_schema = args.validate_schema          # - validate STAC schema
    print_info = True               # - print information
    epsg = args.epsg                # - EPSG code for the GSP file
    gsp_ext = args.gsp_ext          # - extension of the GSP file

    # - Path to sample GSP
    data_dir = Path(args.gsp_path).parent
    print(f"# - Data Directory: {data_dir}")
    # - File Name with extension
    gsp_file = Path(args.gsp_path).name
    # - File Name without extension
    gsp_name = Path(args.gsp_path).stem
    print(f"# - GSP Name: {gsp_name}")
    # - GSP file name - equivalent to product_id in the XML metadata file
    item_id = gsp_name
    # - Collection ID
    collection_id = "ISS_" + item_id.split("_")[1]

    #  - If in put file is not zip raise an error
    if not gsp_file.endswith('.zip'):
        raise ValueError("# - Input file must be a zip archive.")

    # - Check if the GSP file saved with the chose extension
    # - is present inside the zip archive
    try:
        if not ZipHandler.check_file_in_zip(args.gsp_path, gsp_ext):
            raise ValueError(f"# - File with extension {gsp_ext} not found "
                             f"inside the zip archive.")
    except ValueError as e:
        print(f"# - ValueError {str(e)}")
        with zipfile.ZipFile(args.gsp_path, 'r') as zipf:
            print("# - Contents of the zip file:")
            for file in zipf.namelist():
                print(f"# - {file}")
        return

    gsp_path = os.path.join(data_dir,  f'{item_id}.zip')

    print(f"# - GSP Path: {gsp_path}")
    print('# - Loading GSP...')

    # - Load GSP - Vector Data
    s_time = datetime.now()
    if gsp_ext in ['shp', 'csv']:
        gdf_smp = VectorGSP()
        gdf_smp.load_gsp(gsp_path)
    elif gsp_ext in ['tif', 'tiff']:
        gdf_smp = RasterGSP()

        # - Construct the path to the zip file
        zip_path = Path(gsp_path).resolve()

        # - Construct the path to the file inside the zip archive
        raster_path = f'zip+file://{zip_path.as_posix()}!{gsp_name}.{gsp_ext}'
        gdf_smp.load_gsp(raster_path)
    else:
        raise ValueError(f"# - Unsupported GSP file format: {gsp_ext}")

    # - Convert To GeoPandas DataFrame
    xmin, ymin, xmax, ymax = gdf_smp.get_bbox()
    # - Set Bounding Box
    bbox = [xmin, ymin, xmax, ymax]

    # - Extract dataset envelope polygon
    crd = gdf_smp.get_envelope()
    # - Express GPS envelope as a GeoJSON geometry
    env_geometry = {
        "type": "Polygon",
        "coordinates": [crd],
    }

    # - Compute datasets loading time
    e_time = datetime.now()
    print(f"# - Dataframe Loading  Time: {e_time - s_time}")

    # - Read XML Metadata
    meta_dict = extract_xml_from_zip(gsp_path)[0]
    gsp_id = meta_dict['gsp_id']                # - GPS ID [TD3 ID]
    product_id = meta_dict['product_id']        # - Product ID [File Name]
    # - Area of Interest
    aoi = get_aoi_info(meta_dict.get('aoi') or \
                       meta_dict.get('aoi_id'))['aoi_name']

    collection_title = gsp_description(gsp_id)         # - Collection Title
    if gsp_ext in ['shp', 'csv']:
        s_info = return_sensor_info(meta_dict['sensor_id'])
    else:
        # - Raster Data - No sensor info needed
        s_info = ''

    # - Geospatial Product Short Description
    collection_s_descr = collection_title
    # - Derive Dataset Collection from GSP ID
    collection_description = collection_info(gsp_id)

    # - Extract Start and End Dates and convert the into datetime objects
    # - Note: dates from the XML metadata are in the format: YYYYMMDD
    # -       convert them to YYYY-MM-ddT00:00:00Z format.
    s_yyyy, s_mm, s_dd = split_date(meta_dict['start_date'])
    start_date \
        = datetime.strptime(f"{s_yyyy}-{s_mm}-{s_dd}T00:00:00Z",
                            '%Y-%m-%dT00:00:00Z')
    # - Extract End Date
    e_yyyy, e_mm, e_dd = split_date(meta_dict['end_date'])
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
            media_type=f"application/{gsp_ext}",
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
    _ = ProjectionExtension.ext(item, add_if_missing=True)
    if gsp_id not in ["S3-HRDEM-DSM-01", "S3-HRDEM-DTM-01"]:
        _ = SarExtension.ext(item, add_if_missing=True)
        _ = SatExtension.ext(item, add_if_missing=True)

    item.properties["gsp_id"] = gsp_id
    item.properties["product_id"] = product_id
    item.properties["description"] = collection_s_descr
    item.properties["AOI"] = aoi
    item.properties["start_datetime"] \
        = start_date.replace(tzinfo=timezone.utc).isoformat()
    item.properties["end_datetime"] \
        = end_date.replace(tzinfo=timezone.utc).isoformat()

    if gsp_id not in ["S3-HRDEM-DSM-01", "S3-HRDEM-DTM-01"]:
        item.properties["constellation"] = s_info["constellation"]
        item.properties["platform"] = s_info["sensor"]
        item.properties["license"] = "proprietary"
        item.properties["proj:epsg"] = epsg

        item.properties["sat:orbit_state"] = OrbitState("descending")
        item.properties["sar:frequency_band"] = FrequencyBand(s_info["band"])
        item.properties["sar:polarizations"] \
            = [Polarization(x) for x in s_info["polarization"]]
        # item.properties["sar:instrument_mode"] = "IW"
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

    # - If the considered geospatial products belongs to the RasterGSP class
    # - close the raster file before proceeding.
    if isinstance(gdf_smp, RasterGSP):
        gdf_smp.close()

    # - Add JSON STAC file to the zip archive
    # - 1. Item JSON file
    # - 2. Collection JSON file
    # - Then you can call this function like this:
    ZipHandler.update_zip(os.path.join(data_dir, f'{item_id}.zip'),
                          os.path.join(data_dir, f"{item_id}.json"))
    ZipHandler.update_zip(os.path.join(data_dir, f'{item_id}.zip'),
                          os.path.join(data_dir, "collection.json"))
    # - Remove temporary JSON files
    os.remove(os.path.join(data_dir, f"{item_id}.json"))
    os.remove(os.path.join(data_dir, "collection.json"))


# - run main program
if __name__ == '__main__':
    start_time = datetime.now()
    main()
    end_time = datetime.now()
    print(f"# - Computation Time: {end_time - start_time}")
