"""
Set of utilities used to generate anc package geospatial products for
the IRIDE Service Segment - Lot 2.
"""
from typing import List


def gsp_description(gsp_id: str) -> str:
    """
    Returns the description for the GSP product included in the IRIDE
    Service Segment - Lot 2
    :param gsp_id: str - GSP product identifier
    """

    if gsp_id in ['S3-01-SNT-01', 'S3-01-CSM-01', 'S3-01-SAO-01',
                  'S301SNT01', 'S301CSM01', 'S301SAO01']:
        return "Single Geometry Deformation."

    elif gsp_id in ['S3-01-SNT-02', 'S3-01-CSM-02', 'S3-01-SAO-02',
                    'S301SNT02', 'S301CSM02', 'S301SAO02']:
        return "Single Geometry Calibrated Deformation."
    elif gsp_id in ['S3-01-SNT-03', 'S3-01-CSM-03', 'S3-01-SAO-03',
                    'S301SNT03', 'S301CSM03', 'S301SAO03']:
        return "2D Deformation East-West and Vertical Components."
    elif gsp_id in ['S3-01-SNT-04', 'S3-01-CSM-04', 'S3-01-SAO-04',
                    'S301SNT04', 'S301CSM04', 'S301SAO04']:
        return "Active Displacement Areas."
    # - SE-S3-02
    elif gsp_id in ['S3-02-SNT-02', 'S3-02-CSM-02', 'S3-02-SAO-02',
                    'S302SNT02', 'S302CSM02', 'S302SAO02']:
        return "LOS velocities projected along the maximum slope."
    elif gsp_id in ['S3-02-SNT-03', 'S3-02-CSM-03', 'S3-02-SAO-03',
                    'S302SNT03', 'S302CSM03', 'S302SAO03']:
        return "Spatial Anomaly maps."

    # - SE-S3-02
    elif gsp_id in ['S3-02-SNT-04', 'S3-02-CSM-04', 'S3-02-SAO-04',
                    'S302SNT04', 'S302CSM04', 'S302SAO04']:
        return "Temporal Anomaly Maps."
    elif gsp_id in ['S3-02-SNT-05', 'S3-02-CSM-05', 'S3-02-SAO-05',
                    'S302SNT05', 'S302CSM05', 'S302SAO05']:
        return "Automatic identification of unstable slopes."

    # - SE-S3-03
    elif gsp_id in ['S3-03-CHA-01', 'S303CHA01']:
        return "InSAR Statistical Indexes."
    elif gsp_id in ['S3-03-CHA-02', 'S303CHA02']:
        return "3D Velocity Decomposition."
    elif gsp_id in ['S3-03-CHA-03', 'S303CHA03']:
        return ("Identification of Differential Deformation over "
                "Cultural Heritage Structures.")
    elif gsp_id in ['S3-03-CHA-04', 'S303CHA04']:
        return "Temporal Anomaly Maps."
    elif gsp_id in ['S3-03-CHA-05', 'S303CHA05']:
        return ("Intersection of spatio-temporal anomalies "
                "with exposed Cultural heritage.")

    # - SE-S3-04
    elif gsp_id in ['S3-04-SNT-02', 'S3-04-CSM-02', 'S3-04-SAO-02',
                    'S304SNT02', 'S304CSM02', 'S304SAO02']:
        return "Active deformation areas close to infrastructures."
    elif gsp_id in ['S3-04-SNT-03', 'S3-04-CSM-03', 'S3-04-SAO-03',
                    'S304SNT03', 'S304CSM03', 'S304SAO03']:
        return "Anomalous Deformation Areas based on acceleration analysis."

    # - SE-S3-05
    elif gsp_id in ['S3-05-ETQ-01', 'S305ETQ01']:
        return ("Single geometry calibrated deformations resampled "
                "on a medium resolution grid.")
    elif gsp_id in ['S3-05-ETQ-02', 'S305ETQ02']:
        return ("2D calibrated deformations: East-West "
                "and Vertical components.")
    elif gsp_id in ['S3-05-ETQ-03', 'S305ETQ03']:
        return ("Spatial clusterization based on temporal "
                "displacement models.")
    elif gsp_id in ['S3-05-ETQ-04', 'S305ETQ04']:
        return "DInSAR-based co-seismic deformation."
    elif gsp_id in ['S3-05-ETQ-05', 'S305ETQ05']:
        return ("Strategic assets single geometry deformations:"
                " non-calibrated and calibrated.")
    elif gsp_id in ['S3-05-ETQ-06', 'S305ETQ06']:
        return ("Strategic assets 2D deformations:"
                " East-West and vertical components.")
    elif gsp_id in ['S3-05-ETQ-07', 'S305ETQ07']:
        return "Strategic assets PS/DS-based temporal anomalies."

    # - SE-S3-06
    elif gsp_id in ['S3-06-VOL-02', 'S306VOL02']:
        return "Active Deformation Areas Perimeter."
    elif gsp_id in ['S3-06-VOL-03', 'S306VOL03']:
        return ("Identification of Differential Deformation over "
                "Volcanic Areas.")
    elif gsp_id in ['S3-06-VOL-04', 'S306VOL04']:
        return "Temporal Anomaly Maps."
    elif gsp_id in ['S3-06-VOL-05', 'S306VOL05']:
        return "Multi-sensors and multi-geometry Data Fusion."
    elif gsp_id in ['S3-06-VOL-06', 'S306VOL06']:
        return "Change Detection Maps."
    elif gsp_id in ['S3-06-VOL-07', 'S306VOL07']:
        return "InSAR Coherence Maps."
    elif gsp_id in ['S3-06-VOL-08', 'S306VOL08']:
        return "Intersection of spatio-temporal anomalies with exposed assets."

    # - SE-S3-07
    elif gsp_id in ['S3-07-OND-01', 'S307OND01']:
        return ("Single geometry calibrated deformations extracted "
                "for the period of interest.")
    elif gsp_id in ['S3-07-OND-02', 'S307OND02']:
        return ("2D calibrated deformations: "
                "East-West and Vertical components.")
    elif gsp_id in ['S3-07-OND-03', 'S307OND03']:
        return "Landslide Spatial Anomalies."
    elif gsp_id in ['S3-07-OND-04', 'S307OND04']:
        return "Landslide Spatio-Temporal Anomalies."
    elif gsp_id in ['S3-07-OND-05', 'S307OND05']:
        return "Area of influence of active areas from spatial anomalies."
    elif gsp_id in ['S3-07-OND-06', 'S307OND06']:
        return "LOS velocities projected along the maximum slope."
    elif gsp_id in ['S3-07-OND-07', 'S307OND07']:
        return "GNSS time series projected along the PS/DS LOS."
    elif gsp_id in ['S3-07-OND-08', 'S307OND08']:
        return "Volcanic Spatial Statistics."
    elif gsp_id in ['S3-07-OND-09', 'S307OND09']:
        return "InSAR Coherence Maps."

    # - DSM/DTM
    elif gsp_id in ['S3-HRDEM-DSM-01']:
        return "High-Resolution Digital Surface Model (DSM)."
    elif gsp_id in ['S3-HRDEM-DTM-02']:
        return "High-Resolution Digital Terrain Model (DTM)."

    else:
        return ""


def gsp_metadata(gsp_id: str) -> List[str]:
    """
    Returns a list of metadata objects used to create a certain GSP product-
    :param gsp_id: GSP product identifier
    :return: List of metadata objects
    """
    if gsp_id in ['S3-01-SNT-01', 'S3-01-CSM-01', 'S3-01-SAO-01',
                  'S301SNT01', 'S301CSM01', 'S301SAO01']:
        return ['CopDem']

    elif gsp_id in ['S3-01-SNT-02', 'S3-01-CSM-02', 'S3-01-SAO-02',
                    'S301SNT02', 'S301CSM02', 'S301SAO02']:
        return ['CopDem']

    elif gsp_id in ['S3-01-SNT-03', 'S3-01-CSM-03', 'S3-01-SAO-03',
                    'S301SNT03', 'S301CSM03', 'S301SAO03']:
        return ['CopDem']

    elif gsp_id in ['S3-01-SNT-04', 'S3-01-CSM-04', 'S3-01-SAO-04',
                    'S301SNT04', 'S301CSM04', 'S301SAO04']:
        return ['CopDem', 'OpenStreetMap']

    elif gsp_id in ['S3-02-SNT-02', 'S3-02-CSM-02', 'S3-02-SAO-02',
                    'S302SNT02', 'S302CSM02', 'S302SAO02']:
        return ['Tinitaly-10']

    elif gsp_id in ['S3-02-SNT-04', 'S3-02-CSM-04', 'S3-02-SAO-04',
                    'S302SNT04', 'S302CSM04', 'S302SAO04']:
        return ['Tinitaly-10']

    elif gsp_id in ['S3-02-SNT-05', 'S3-02-CSM-05', 'S3-02-SAO-05',
                    'S302SNT05', 'S302CSM05', 'S302SAO05']:
        return ['Tinitaly-10']

    elif gsp_id in ['S3-04-SNT-02', 'S3-04-CSM-02', 'S3-04-SAO-03',
                    'S304SNT02', 'S304CSM02', 'S304SAO04',
                    'S3-04-SNT-03', 'S3-04-CSM-03', 'S3-04-SAO-03',
                    'S304SNT03', 'S304CSM03', 'S304SAO03']:

        return ['OpenStreetMap', 'CopDem']

    elif gsp_id in ['S3-HRDEM-DSM-01', 'S3-HRDEM-DTM-02']:
        return ['Available DSM/DTM', 'Aerial_Survey', 'S3-NEO-I22']

    else:

        return []


def gsp_d_type(gsp_id: str) -> str:
    """
    Returns the data type for the GSP product included in the IRIDE
    Args:
        gsp_id: GSP ID - as reported in TD3
    Returns: Product type as a string
    """
    if gsp_id in ['S3-01-SNT-01', 'S3-01-CSM-01', 'S3-01-SAO-01',
                  'S301SNT01', 'S301CSM01', 'S301SAO01',
                  'S3-01-SNT-02', 'S3-01-CSM-02', 'S3-01-SAO-02',
                  'S301SNT02', 'S301CSM02', 'S301SAO02',
                  'S3-01-SNT-03', 'S3-01-CSM-03', 'S3-01-SAO-03',
                  'S301SNT03', 'S301CSM03', 'S301SAO03',
                  'S3-02-SNT-02', 'S3-02-CSM-02', 'S3-02-SAO-02',
                  'S302SNT02', 'S302CSM02', 'S302SAO02',
                  'S3-02-SNT-04', 'S3-02-CSM-04', 'S3-02-SAO-04',
                  'S302SNT04', 'S302CSM04', 'S302SAO04',
                  'S3-02-SNT-05', 'S3-02-CSM-05', 'S3-02-SAO-05',
                  'S302SNT05', 'S302CSM05', 'S302SAO05',
                  'S3-03-CHA-02', 'S303CHA02', 'S3-03-CHA-04', 'S303CHA04',
                  'S3-04-SNT-02', 'S3-04-CSM-02', 'S3-04-SAO-03',
                  'S304SNT02', 'S304CSM02', 'S304SAO04',
                  'S3-04-SNT-03', 'S3-04-CSM-03', 'S3-04-SAO-03',
                  'S304SNT03', 'S304CSM03', 'S304SAO03',
                  'S3-05-ETQ-01', 'S305ETQ01', 'S3-05-ETQ-02', 'S305ETQ02',
                  'S3-05-ETQ-03', 'S305ETQ03', 'S3-05-ETQ-06', 'S305ETQ06',
                  'S3-05-ETQ-07', 'S305ETQ07',
                  'S3-06-VOL-02', 'S306VOL02', 'S3-06-VOL-04', 'S306VOL04',
                  'S3-06-VOL-05', 'S306VOL05',
                  'S3-07-OND-01', 'S307OND01', 'S3-07-OND-02', 'S307OND02',
                  'S3-07-OND-07', 'S307OND07',
                  ]:
        return "ESRI Shapefile (Geometry: Points) + CSV"

    elif gsp_id in ['S3-01-SNT-04', 'S3-01-CSM-04', 'S3-01-SAO-04',
                    'S301SNT04', 'S301CSM04', 'S301SAO04',
                    'S3-02-SNT-04', 'S3-02-CSM-04', 'S3-02-SAO-04',
                    'S302SNT04', 'S302CSM04', 'S302SAO04',
                    'S3-03-CHA-01', 'S303CHA01', 'S3-03-CHA-03', 'S303CHA03',
                    'S3-03-CHA-05', 'S303CHA05', 'S3-06-VOL-02', 'S306VOL02',
                    'S3-06-VOL-08', 'S306VOL08',
                    'S3-07-OND-06', 'S307OND06', 'S3-07-OND-08', 'S307OND08'
                    ]:
        return "ESRI Shapefile (Geometry: Polygon)"

    elif gsp_id in ['S3-05-ETQ-04', 'S305ETQ04', 'S3-06-VOL-06', 'S306VOL06',
                    'S3-06-VOL-07', 'S306VOL07']:
        return "GeoTiff disp. Map + XML"

    elif gsp_id in ['S3-06-VOL-02', 'S306VOL02', 'S3-07-OND-03', 'S307OND03',
                    'S3-07-OND-04', 'S307OND04', 'S3-07-OND-05', 'S307OND05',
                    'S3-07-OND-09', 'S307OND09']:
        return "ESRI Shapefile (Geometry: Polygon / Points) + CSV"

    elif gsp_id in ['S3-06-VOL-08', 'S306VOL08']:
        return "ESRI Shapefile (Geometry: Polygon / Polylines) + CSV"

    elif gsp_id in ['S3-HRDEM-DSM-01', 'S3-HRDEM-DTM-02']:
        return "GeoTIFF + XML"

    else:
        return "NA"
