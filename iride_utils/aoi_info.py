"""
Written by Enrico Ciraci' - February 2024
Return IRIDE AOIs information
"""


def get_aoi_info(aoi: str) -> dict:
    """
    Return AOI information
    :param aoi: AOI Name [can be the extended name or aoi tag]
    :return: Dictionary with AOI information
    """
    # - convert to all lower case
    aoi = aoi.lower()

    if aoi in ['nocera_terinese', 'ntr', 'nocera terinese']:
        aoi_tag = 'NTR'
        aoi_name = 'A2 - Nocera Terinese'

    elif aoi in ['palermo', 'pal']:
        aoi_tag = 'PAL'
        aoi_name = 'Palermo'

    elif aoi in ['brennero', 'brn']:
        aoi_tag = 'BRN'
        aoi_name = 'Brennero Area'

    elif aoi in ['belluno', 'bel']:
        aoi_tag = 'BEL'
        aoi_name = 'Belluno Area'

    elif aoi in ['cortina', 'crt']:
        aoi_tag = 'CRT'
        aoi_name = 'Cortina'

    elif aoi in ['norcia', 'nri']:
        aoi_tag = 'NRI'
        aoi_name = 'Norcia'

    elif aoi in ['pistoia', 'pst']:
        aoi_tag = 'PST'
        aoi_name = 'Pistoia'

    elif aoi in ['mattinata', 'mti']:
        aoi_tag = 'mti'
        aoi_name = 'Mattinata'

    elif aoi in ['colli_albani', 'coa']:
        aoi_tag = 'coa'
        aoi_name = 'Colli ALbani Area'

    elif aoi in ['Vulcano', 'vla']:
        aoi_tag = 'VLA'
        aoi_name = 'Vulcano Island'

    # - Italian Regions
    elif aoi in ['calabria', 'cal']:
        aoi_tag = 'CAL'
        aoi_name = 'Calabria'

    elif aoi in ['sicilia', 'sic']:
        aoi_tag = 'SIC'
        aoi_name = 'Sicilia'

    elif aoi in ['basilicata', 'bas']:
        aoi_tag = 'BAS'
        aoi_name = 'Basilicata'

    elif aoi in ['puglia', 'pug']:
        aoi_tag = 'PUG'
        aoi_name = 'Puglia'

    elif aoi in ['campania', 'cam']:
        aoi_tag = 'CAM'
        aoi_name = 'Campania'

    elif aoi in ['molise', 'mol']:
        aoi_tag = 'MOL'
        aoi_name = 'Molise'

    elif aoi in ['abruzzo', 'abr']:
        aoi_tag = 'ABR'
        aoi_name = 'Abruzzo'

    elif aoi in ['lazio', 'laz']:
        aoi_tag = 'LAZ'
        aoi_name = 'Lazio'

    elif aoi in ['umbria', 'umb']:
        aoi_tag = 'UMB'
        aoi_name = 'Umbria'

    elif aoi in ['marche', 'mar']:
        aoi_tag = 'MAR'
        aoi_name = 'Marche'

    elif aoi in ['emilia_romagna', 'era']:
        aoi_tag = 'ERA'
        aoi_name = 'Emilia Romagna'

    elif aoi in ['toscana', 'tos']:
        aoi_tag = 'TOS'
        aoi_name = 'Toscana'

    elif aoi in ['lombardia', 'lom']:
        aoi_tag = 'LOM'
        aoi_name = 'Lombardia'

    elif aoi in ['piemonte', 'pie']:
        aoi_tag = 'PIE'
        aoi_name = 'Piemonte'

    elif aoi in ['sardegna', 'sar']:
        aoi_tag = 'SAR'
        aoi_name = 'Sardegna'

    elif aoi in ['trentino', 'taa']:
        aoi_tag = 'TAA'
        aoi_name = 'Trentino Alto Adige'

    elif aoi in ['veneto', 'ven']:
        aoi_tag = 'VEN'
        aoi_name = 'Veneto'

    elif aoi in ['friuli_venezia_giulia', 'fvg', 'friuli']:
        aoi_tag = 'FVG'
        aoi_name = 'Friuli Venezia Giulia'

    elif aoi in ['liguria', 'lig']:
        aoi_tag = 'LIG'
        aoi_name = 'Liguria'

    elif aoi in ['valle_d_aosta', 'vda']:
        aoi_tag = 'VDA'
        aoi_name = 'Valle d\'Aosta'

    elif aoi in ['etns', 'etn']:
        aoi_tag = 'ETN'
        aoi_name = 'ETN'

    else:

        raise ValueError(f"AOI {aoi} not found.")

    return {'aoi_tag': aoi_tag, 'aoi_name': aoi_name}
