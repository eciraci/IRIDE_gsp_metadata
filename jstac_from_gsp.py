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
# - Third-Party Dependencies
import pystac
import geopandas as gpd
from pystac.extensions.sar import SarExtension, FrequencyBand, Polarization
from pystac.extensions.sat import SatExtension, OrbitState
from pystac.extensions.projection import ProjectionExtension

from xml_utils import extract_xml_from_zip


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


def main() -> None:
    # - Set Parameters
    overwrite = True            # - overwrite existing files
    validate_schema = False     # - validate STAC schema
    epsg = 4326                 # - EPSG code for the GSP file
    collection_id = "ISS_S304SNT02"
    gsp_ext = "shp"       # - extension of the GSP file
    collection_title = "Critical Infrastructures Monitoring"
    collection_description \
        = ("This collection includes products for analyzing "
           "deformation phenomena (e.g., landslides, subsidence, etc.) "
           "associated with critical infrastructures and their surroundings")

    # - path to sample GSP
    data_dir = os.path.join(os.path.expanduser('~'), 'Desktop',
                            'Scripts', 'lot2')
    # - GSP file name - equivalent to product_id in the XML metadata file
    gsp_name = 'ISS_S304SNT02_20180705_20230627_095BRND_01'
    item_id = gsp_name
    zip_path = os.path.join(data_dir,  f'{gsp_name}.zip')
    gsp_path = os.path.join(data_dir, f'{gsp_name}.zip!{gsp_name}.{gsp_ext}')

    print(f"# - GSP Path: {gsp_path}")
    print('# - Loading GSP...')

    # - read GSP
    s_time = datetime.now()
    gdf_smp = gpd.read_file(gsp_path).to_crs(epsg=epsg)

    # - Compute Loading Time
    e_time = datetime.now()
    # - Initialize Processing Time
    # - For the first IRIDE data release, set this value equal to
    # - the 15th on March 2024
    proc_datetime = datetime(2024, 3, 15, 0, 0, 0, 0, timezone.utc)

    # - Convert To GeoPandas DataFrame
    total_bounds = gdf_smp.total_bounds
    xmin, ymin, xmax, ymax = total_bounds

    # - Set Bounding Box
    bbox = [xmin, ymin, xmax, ymax]

    # - extract dataset envelope polygon
    envelope = gpd.GeoSeries([gdf_smp.unary_union.envelope],
                             crs=gdf_smp.crs).iloc[0].exterior.coords.xy
    xs = envelope[0]
    ys = envelope[1]
    crd = list(zip(xs, ys))

    env_geometry = {
        "type": "Polygon",
        "coordinates": [crd],
    }
    print(f"# - Extract Dataset Total Bounds: {total_bounds}")

    e_time = datetime.now()
    print(f"# - Dataframe Loading  Time: {e_time - s_time}")

    # - Read XML Metadata
    meta_dict = extract_xml_from_zip(zip_path)[0]
    # - Extract Start and End Dates and convert the into datetime objects
    # - Note: dates from the XML metadata are in the format: YYYYMMDD
    # -       convert them to YYYY-MM-ddT00:00:00Z" format
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
    time_interval = [start_date, end_date]

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
        title="Critical infrastructures monitoring",
        extent=extent
    )

    #  - Validate activation collection format
    print("# - Validate Activation Collection:")
    print(pystac.validation.validate(activation_collection))
    # - Write Activation Collection to JSON file
    pystac.write_file(
        obj=activation_collection,
        include_self_link=False,
        dest_href=os.path.join(item_id, "collection.json")
    )

    item = pystac.Item(
        id=item_id,
        geometry=env_geometry,
        bbox=bbox,
        properties={},
        datetime=proc_datetime,
        stac_extensions=[],
        collection=collection_id,
    )

    # - Add GSP Assets
    item.add_asset(
        "GSP",
        asset=pystac.Asset(
            href=f"./{gsp_name}.{gsp_ext}",
            media_type="application/{gsp_ext}",
            title=f"Lot 2 Geospatial Product: {item.id}",
            description=f"Single Geometry Deformation",
            roles=["data", "visual"],
        ),
    )

    # -  Add GSP Metadata Asset
    item.add_asset(
        "GSP-Metadata",
        asset=pystac.Asset(
            href=f"./{item_id}.xml",
            media_type="application/xml",
            title="ISO-19115 metadata for "
                  "ISS_S304SNT02_20180702_20230624_051NTRD_01",
            description="ISO-19115 metadata for "
                        "ISS_S304SNT02_20180702_20230624_051NTRD_01",
            roles=["metadata", "iso-19115"],
        ),
    )

    item.stac_extensions = [
        "https://stac-extensions.github.io/projection/v1.1.0/schema.json",
        "https://stac-extensions.github.io/sar/v1.0.0/schema.json",
        "https://stac-extensions.github.io/sat/v1.0.0/schema.json"]

    item.properties["gsp_id"] = "S3-04-SNT-02"
    item.properties[
        "product_id"] = "ISS_S304SNT02_20180702_20230624_051NTRD_01"
    item.properties[
        "description"] = ("Active Displacement Areas Closed "
                          "to Critical Infrastructure")
    item.properties["AOI"] = "NTR"
    item.properties["start_datetime"] = start_date
    item.properties["end_datetime"] = end_date
    item.properties["constellation"] = "Sentinel-1"
    item.properties["platform"] = "Sentinel-1A"
    item.properties["license"] = "TBD"
    item.properties["proj:epsg"] = 4326
    item.properties["sat:orbit_state"] = "descending"
    item.properties["sar:frequency_band"] = "C"
    item.properties["sar:polarizations"] = ["VV"]
    item.properties["sar:instrument_mode"] = "IW"
    item.properties["sar:product_type"] = "SLC"
    item.properties["providers"] = [{"name": "eGeos",
                                     "roles": ["producer", "processor"],
                                     "url": "https://www.e-geos.it/"}
                                    ]
    #item.properties["datetime"] = proc_datetime

    item.to_dict()

    # - Processing Properties
    #item.properties["processing:level"] = "GRD Post Processing"

    # - Add STAC Extensions
    #proj_ext = ProjectionExtension.ext(item, add_if_missing=True)
    #sar_ext = SarExtension.ext(item, add_if_missing=True)
    #sat_ext = SatExtension.ext(item, add_if_missing=True)

    # - Add Projection Extension Properties
    #proj_ext.epsg = 4326
    # - Add Satellite Extension Properties
    #sat_ext.orbit_state = OrbitState("descending")
    # - Add SAR Extension Properties
    #sar_ext.frequency_band = FrequencyBand("C")
    #sar_ext.polarizations = [Polarization("VV"), Polarization("VH")]
    #sar_ext.processing_level = "L2"
    #sar_ext.instrument_mode = "IW"

    # - Add Provider Information
    #item.common_metadata.providers = [
    #    pystac.Provider(
    #        name="eGeos",
    #        url="https://www.e-geos.it/",
    #        roles=[pystac.ProviderRole.PRODUCER,
    #               pystac.ProviderRole.PROCESSOR],
    #    )
    #]

    # - Add Link to Collection
    item.add_link(link=pystac.Link(rel="collection", target="collection.json"))

    # - PySTAC does not allow to validate the item
    print(item.validate())

    """
    # - Validate Item
    if validate_schema:
        item.validate()

    # catalog.add_item(item)
    # catalog.describe()
    # - Write Item to JSON file
    pystac.write_file(obj=item, include_self_link=False,
                      dest_href=os.path.join(data_dir, f"{gsp_name}.json"))

    with zipfile.ZipFile(os.path.join(data_dir, f'{gsp_name}.zip'),
                         'r') as zipf:
        zip_names = zipf.namelist()
    if f"{gsp_name}.json" in zip_names and overwrite:
        update_zip(os.path.join(data_dir,  f'{gsp_name}.zip'),
                   os.path.join(data_dir, f"{gsp_name}.json"))
    else:
        with zipfile.ZipFile(
                os.path.join(data_dir, f'{gsp_name}.zip'),
                'w') as zip_f:
            # -
            source_path = os.path.join(data_dir, f"{gsp_name}.json")
            destination = f"{gsp_name}.json"
            zip_f.write(source_path, destination)
    """

# - run main program
if __name__ == '__main__':
    start_time = datetime.now()
    main()
    end_time = datetime.now()
    print(f"# - Computation Time: {end_time - start_time}")
