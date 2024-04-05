"""
Written by Enrico Ciraci' - April 2024

Return IRIDE Lot 2 - Generic Service Value Chain Descrption
"""


def collection_info(gsp_id: str) -> str:
    """
    Return IRIDE Lot 2 Product Collections Information
    :param gsp_id: str - GSP product identifier
    """
    if (gsp_id.startswith('S301') or gsp_id.startswith('S3-01') or
            gsp_id.startswith('SE-S3-01') or gsp_id.startswith('SES301')):
        # - Service Value Chain: SE-S3-01
        # - Ground
        return ("The SVC SE-S3-01 produces ground deformation measurements "
                "over the Italian territory using multi-temporal "
                "interferometric techniques (Persistent and Distributed "
                "Scatterers). These products are generated systematically "
                "for different periods. During the precursor phase of "
                "the project, the consortium will perform interferometric "
                "analyses employing data from the Italian Space Agency (ASI)"
                " COSMO-SkyMed, the European Space Agency (ESA) Sentinel-1, "
                "and the Argentinian National Space Activities "
                "Commission (CONAE) SAOCOM missions. Basic products are "
                "afterward processed by this and the other service value "
                "chains to create higher-level products.")

    elif (gsp_id.startswith('S302') or gsp_id.startswith('S3-02') or
          gsp_id.startswith('SE-S3-02') or gsp_id.startswith('SES302')):
        # - Service Value Chain: SE-S3-02
        # - Landslides Monitoring
        return ("The SVC SE-S3-02 is aimed at monitoring large areas affected "
                "by landslide phenomena in deferred time, providing "
                "indications about possible cinematic changes, possibly "
                "improving the classification and the zonation of the "
                "phenomena.")

    elif (gsp_id.startswith('S303') or gsp_id.startswith('S3-03') or
          gsp_id.startswith('SE-S3-03') or gsp_id.startswith('SES303')):
        # - Service Value Chain: SE-S3-03
        # - Cultural Heritage Monitoring
        return ("The SVC SE-S3-03 analyzes deformation phenomena in cultural "
                "heritage structures and their surroundings. The service aims "
                "to improve our understanding of ground displacement "
                "processes that affect cultural heritage (e.g., landslides, "
                "subsidence, etc.) by using InSAR high-resolution data "
                "observations and providing instruments capable of producing "
                "spatiotemporal anomalies, differential deformation maps,"
                "and other useful statistical information.")

    elif (gsp_id.startswith('S304') or gsp_id.startswith('S3-04') or
            gsp_id.startswith('SE-S3-04') or gsp_id.startswith('SES304')):
        # - Service Value Chain: SE-S3-04
        # - Critical Infrastructure Monitoring
        return ("The SVC SE-S3-04 is aimed at monitoring critical "
                "infrastructures (e.g., bridges, dams, railways, highways, "
                "etc.) by analyzing deformation phenomena that could affect "
                "their stability and functionality. The service aims to "
                "provide improve our understanding of ground displacement "
                "processes (e.g., landslides, subsidence, etc.) that affect "
                "critical infrastructure stability")

    elif (gsp_id.startswith('S305') or gsp_id.startswith('S3-05') or
            gsp_id.startswith('SE-S3-05') or gsp_id.startswith('SES305')):
        # - Service Value Chain: SE-S3-05
        # - Monitoring of seismic wide areas during inter-seismic phase
        return ("The SVC SE-S3-05 aims at providing high-resolution monitoring"
                " of active crustal strain in seismic regions during "
                "co-seismic, post-seismic, and inter-seismic periods related "
                "to regional geodynamics processes."
                "The monitoring is based on the analysis (including spatial "
                "clustering and fit of temporal displacement models) of PS/DS "
                "displacement time series calibrated with geodetic data from "
                "regional GNSS networks.")

    elif (gsp_id.startswith('S306') or gsp_id.startswith('S3-06') or
            gsp_id.startswith('SE-S3-06') or gsp_id.startswith('SES306')):
        # - Service Value Chain: SE-S3-06
        # - Volcanic Areas Monitoring
        return ("The SVC SE-S3-06 analyzes deformation phenomena in Italian "
                "volcanic areas. The service goal is to improve our "
                "understanding of ground displacement processes affecting"
                " volcanoes using InSAR high-resolution data observations. "
                "The service also provides instruments that can be used to "
                "compute spatio-temporal anomalies, differential deformation "
                "maps, and other statistical information. The chain delivers "
                "ground deformation maps obtained by combining multi-geometry "
                "radar measurements from the Italian Space Agency (ASI) "
                "COSMO-SkyMed and the European Space Agency "
                "(ESA) Sentinel-1 missions..")

    elif (gsp_id.startswith('S307') or gsp_id.startswith('S3-07') or
            gsp_id.startswith('SE-S3-07') or gsp_id.startswith('SES307')):
        # - Service Value Chain: SE-S3-07
        # - On-Demand Monitoring
        return ("The Service Value Chain aims at providing high-resolution "
                "ground motion monitoring services in deferred time that "
                "can be activated on-demand over specific landslide and "
                "volcanic areas where active deformation has been detected."
                "The monitoring is based on the analysis of PS/DS "
                "displacement time series non-calibrated and calibrated "
                "with geodetic data from regional GNSS networks and coherence "
                "information. The products highlight the deformation areas and"
                " the kinematic characteristics of landslides and volcanic "
                "activities through the spatio-temporal analysis of ground"
                " motion measurements. The spatial coherence map covering the "
                "crisis period supports the detection of areas "
                "covered by the lava flow.")

    elif gsp_id.startswith('DSM') or gsp_id.startswith('DTM'):
        # - Service Value Chain: DSM-DTM
        # - High-Resolution Digital Surface Model (DSM)
        # -  and a Digital Terrain Model (DTM)
        return ("the SVC devoted to generating a High-Resolution Digital "
                "Surface Model (DSM) and a Digital Terrain Model (DTM) "
                "covering the Italian territory. This SVC is, therefore, "
                "focused on generating a general-use product, i.e., a product "
                "that will be used as input to the other SVCs but won’t "
                "deliver a production infrastructure and the system. "
                "For this reason, the software modules described in the "
                "following paragraphs are not included among those used in "
                "the Geoprocessing macroblock of the service value chain "
                "workflow.")

    # - Unknown GSP identifier - raise ValueError
    raise ValueError(f"Unknown GSP identifier: {gsp_id}")
