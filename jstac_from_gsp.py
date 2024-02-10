#!/usr/bin/env python
u"""
Written by:  Enrico Ciraci' - February 2024

Add a JSON Stack Item to an existing Geospatial Products (GSP) file
saved inside a .zip file.
"""
# - Python Dependencies
import os
from datetime import datetime, timezone
# - Third-Party Dependencies
import pystac
import geopandas as gpd
import dask_geopandas as dgpd
from pystac.extensions.sar import SarExtension, FrequencyBand, Polarization
from pystac.extensions.sat import ItemSatExtension, SatExtension, OrbitState
from pystac.extensions.projection import ProjectionExtension


def main() -> None:

    validate_schema = False  # - validate STAC schema

    # - path to sample GSP
    data_dir = os.path.join(os.path.expanduser('~'), 'Desktop')
    gsp_name = 'ISS_S301SNT01_20180712_20230622_022D0865IW2_01'
    # gsp_path = os.path.join(data_dir, f'{gsp_name}.csv')
    # gsp_path = os.path.join(data_dir,  f'{gsp_name}.zip!{gsp_name}.csv')
    gsp_path = os.path.join(data_dir,  f'{gsp_name}.parquet')

    print(f"# - GSP Path: {gsp_path}")
    print('# - Loading GSP...')

    # - read GSP
    s_time = datetime.now()
    # gdf_smp = dgpd.read_file(gsp_path, npartitions=4)
    gdf_smp = dgpd.read_parquet(gsp_path, npartitions=4)

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

    # - Plot GSP
    # import matplotlib.pyplot as plt
    # fig, ax = plt.subplots()
    # gdf_smp.plot(ax=ax, c=gdf_smp['height'], cmap='viridis', legend=True)
    # plt.show()
    #
    # collection = "iss-se-s3-01"
    # collection = pystac.Collection(id='wv3-images',
    #                                description='Spacenet 5 images over Moscow',
    #                                extent=collection_extent,
    #                                license='CC-BY-SA-4.0')

    catalog = pystac.Catalog(
        id='Paranapanema',
        description='Water masks from Paranapanema basin',
        stac_extensions=[
            'https://stac-extensions.github.io/projection/v1.0.0/schema.json',
            'https://stac-extensions.github.io/sat/v1.0.0/schema.json',
            'https://stac-extensions.github.io/sar/v1.0.0/schema.json',
        ]
    )

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

    catalog.add_item(item)
    catalog.describe()
    # - Write Item to JSON file
    pystac.write_file(obj=item, include_self_link=False,
                      dest_href=os.path.join(data_dir, f"{gsp_name}.json"))

    import zipfile
    with zipfile.ZipFile(os.path.join(data_dir, f'{gsp_name}.zip'),
                         'r') as zipf:
        info = zipf.infolist()
        zip_names = zipf.namelist()
    print(f"# - Zip Info: {info}")
    print(zip_names)
    # with zipfile.ZipFile(os.path.join(data_dir,  f'{gsp_name}.zip'), 'a') as zipf:
    #     # -
    #     source_path = os.path.join(data_dir, f"{gsp_name}.json")
    #     destination = f"{gsp_name}.json"
    #     zipf.write(source_path, destination)

    # - generate xml metadata inspired by ISO-19115
    # import xml.etree.ElementTree as ET
    # root = ET.Element("metadata")
    # ET.SubElement(root, "title").text = f"{gsp_name}"
    # ET.SubElement(root, "abstract").text = "This is a sample abstract"
    # tree = ET.ElementTree(root)
    # tree.write(os.path.join(data_dir, f"{gsp_name}.xml"))
    # from stac_validator import stac_validator
    # stac = stac_validator.StacValidate(os.path.join(data_dir, f"{gsp_name}.json"))
    # stac.run()
    # print(stac.message)



# - run main program
if __name__ == '__main__':
    start_time = datetime.now()
    main()
    end_time = datetime.now()
    print(f"# - Computation Time: {end_time - start_time}")