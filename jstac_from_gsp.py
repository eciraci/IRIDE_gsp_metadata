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
from datetime import datetime, timezone
import zipfile
# - Third-Party Dependencies
import pystac
import geopandas as gpd
import dask_geopandas as dgpd
from pystac.extensions.sar import SarExtension, FrequencyBand, Polarization
from pystac.extensions.sat import ItemSatExtension, SatExtension, OrbitState
from pystac.extensions.projection import ProjectionExtension


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
    overwrite = True  # - overwrite existing files
    validate_schema = False  # - validate STAC schema

    # - path to sample GSP
    data_dir = os.path.join(os.path.expanduser('~'), 'Desktop')
    gsp_name = 'ISS_S301SNT01_20180712_20230622_022D0865IW2_01'

    gsp_path = os.path.join(data_dir, f'{gsp_name}.csv')
    gsp_path = os.path.join(data_dir,  f'{gsp_name}.zip!{gsp_name}.csv')
    # gsp_path = os.path.join(data_dir,  f'{gsp_name}.parquet')

    print(f"# - GSP Path: {gsp_path}")
    print('# - Loading GSP...')

    # - read GSP
    s_time = datetime.now()
    gdf_smp = dgpd.read_file(gsp_path, npartitions=4)
    # gdf_smp = dgpd.read_parquet(gsp_path, npartitions=4)

    geometry = dgpd.points_from_xy(gdf_smp, x='longitude', y='latitude',
                                   crs="EPSG:4326")
    gdf_smp = dgpd.from_dask_dataframe(gdf_smp, geometry=geometry)
    gdf_smp = gdf_smp.set_crs("EPSG:4326")

    e_time = datetime.now()

    print(f"# - Load Time: {e_time - s_time}")
    # - Convert To GeoPandas DataFrame
    gdf_smp = gdf_smp.compute()
    total_bounds = gdf_smp.total_bounds
    xmin, ymin, xmax, ymax = total_bounds
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
    print(f"# - Conversion Time: {e_time - s_time}")
    # - save GSP to parquet
    gdf_smp.to_parquet(os.path.join(data_dir, f'{gsp_name}.parquet'))

    # - Create STAC Item
    # collection = "iss-se-s3-01"
    # collection = pystac.Collection(id='wv3-images',
    #                                description='Spacenet 5 images over Moscow',
    #                                extent=collection_extent,
    #                                license='CC-BY-SA-4.0')

    # catalog = pystac.Catalog(
    #     id='Paranapanema',
    #     description='Water masks from Paranapanema basin',
    #     stac_extensions=[
    #         'https://stac-extensions.github.io/projection/v1.0.0/schema.json',
    #         'https://stac-extensions.github.io/sat/v1.0.0/schema.json',
    #         'https://stac-extensions.github.io/sar/v1.0.0/schema.json',
    #     ]
    # )

    print(f"# - Geometry: {env_geometry}")
    bbox = [xmin, ymin, xmax, ymax]

    item = pystac.Item(
        id=f"{gsp_name}",
        geometry=env_geometry,
        bbox=bbox,
        properties={"burst_id": "087-0208-IW1-VV",
                    "comment": "The following properties are optional "
                               "but are useful to have.",
                    },
        datetime=datetime.now(timezone.utc),
        start_datetime=datetime.now(timezone.utc),
        end_datetime=datetime.now(timezone.utc),
        stac_extensions=[],
        # collection=collection,
    )

    # - Add Common Metadata
    item.common_metadata.constellation = "Sentinel-1"
    item.common_metadata.platform = "ESA Sentinel"
    item.common_metadata.porcessing_facility\
        = "eGeos Via Tiburtina, 965, 00156 Roma RM"
    item.common_metadata.license = "TBD"

    # - Processing Properties
    # item.properties["processing:level"] = "GRD Post Processing"

    # - Add STAC Extensions
    proj_ext = ProjectionExtension.ext(item, add_if_missing=True)
    sar_ext = SarExtension.ext(item, add_if_missing=True)
    sat_ext = SatExtension.ext(item, add_if_missing=True)

    # - Add Projection Extension Properties
    proj_ext.epsg = 4326
    # - Add Satellite Extension Properties
    sat_ext.orbit_state = OrbitState("descending")
    # - Add SAR Extension Properties
    sar_ext.frequency_band = FrequencyBand("C")
    sar_ext.polarizations = [Polarization("VV"), Polarization("VH")]
    sar_ext.processing_level = "L2"
    sar_ext.instrument_mode = "IW"

    # - Add Provider Information
    item.common_metadata.providers = [
        pystac.Provider(
            name="eGeos",
            url="https://www.e-geos.it/",
            roles=[pystac.ProviderRole.PRODUCER,
                   pystac.ProviderRole.PROCESSOR],
        )
    ]

    # - Add Assets
    item.add_asset(
        "GSP",
        asset=pystac.Asset(
            href=f"./{gsp_name}.csv",
            media_type="application/csv",
            title=f"Lot 2 Geospatial Product: {item.id}",
            description=f"Single Geometry Deformation",
            roles=["data"],
        ),
    )

    item.add_asset(
        "GSP-Metadata",
        asset=pystac.Asset(
            href=f"./{gsp_name}.xml",
            media_type="application/xml",
            title=f"ISO-19115 metadata for {item.id}",
            description=f"ISO-19115 metadata for {item.id}",
            roles=["iso-19115"],
        ),
    )

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


# - run main program
if __name__ == '__main__':
    start_time = datetime.now()
    main()
    end_time = datetime.now()
    print(f"# - Computation Time: {end_time - start_time}")