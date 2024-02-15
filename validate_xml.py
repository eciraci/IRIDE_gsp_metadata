#!/usr/bin/env python
"""
Written by Enrico Ciraci' - February 2024

This script reads an XML file and an XSD file and validates the XML file.

Python Dependencies:
    - datetime: to measure the computation time
    - lxml: to parse the XML and XSD files
    - pathlib: to handle file paths
"""
# - Python Dependencies
from datetime import datetime
from lxml import etree
from pathlib import Path


def validate_xml_against_schema(xml_input: str | Path,
                                xsd_input: str | Path) -> None:
    xsd_tree = etree.parse(xsd_input)
    xsd_schema = etree.XMLSchema(xsd_tree)
    xml_tree = etree.parse(xml_input)
    try:
        xsd_schema.assertValid(xml_tree)
        print("The XML file is valid against the schema.")
    except etree.DocumentInvalid as e:
        print("The XML file is not valid against the schema. Error:", str(e))


if __name__ == '__main__':
    start_time = datetime.now()
    xml_path = Path('./templates/SE-S3-01/SNT/'
                    'ISS_S301SNT04_20180701_20231231_PUGE_01.xml')
    xsd_path = Path('./templates/SE-S3-01/SNT/'
                    'ISS_S301SNT04_20180701_20231231_PUGE_01.xsd')
    validate_xml_against_schema(xml_path, xsd_path)
    print(f"Computation Time: {datetime.now() - start_time}")
