"""
Written by: Enrico Cirac' - February 2024
Utility functions to work with xml files.

Python Dependencies:
- zipfile: Work with zip archives
- xml.etree.ElementTree: XML parsing and generation
- xml.dom.minidom: Pretty print xml files
- typing: Type hints
- lxml: XML validation against a schema
- pathlib: Work with file paths
"""
import zipfile
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString
from lxml import etree
from typing import Union, Dict, List
from pathlib import Path


def xml_to_dict(element: ET.Element) -> Union[Dict, str]:
    """
    Convert a xml string to a dictionary
    :param element: ET.Element
    :return: python dictionary
    """
    if len(element) == 0:  # if the element has no children
        return element.text
    return {child.tag: xml_to_dict(child) for child in element}


def extract_xml_from_zip(zip_file_path: str) -> List[Dict]:
    """
    Extract the xml files from the zip file and convert them to dictionaries
    Note: this function assumes that no repeated keys are present
        in the xml file.
    :param zip_file_path: absolute path to the zip file
    :return: list of python dictionaries
    """
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zipf:
            xml_dicts = []
            for filename in zipf.namelist():
                if filename.endswith('.xml'):
                    with zipf.open(filename) as xml_file:
                        xml_string = xml_file.read().decode('utf-8')
                        root = ET.fromstring(xml_string)
                        xml_dict = xml_to_dict(root)
                        xml_dicts.append(xml_dict)
            return xml_dicts
    except zipfile.BadZipFile:
        print(f"Error: The file {zip_file_path} is not a zip "
              f"file or it is corrupted.")
    except FileNotFoundError:
        print(f"Error: The file {zip_file_path} does not exist.")


def dict_to_xml(input_dict: Dict, filename: str) -> None:
    """
    Convert a dictionary to an xml file
    :param input_dict: dictionary to convert
    :param filename: name of the output xml file
    """
    # Create the root element
    root = Element('root')

    # Function to convert dictionary items to xml elements
    def dict_to_elem(element, dictionary):
        for key in dictionary:
            child = SubElement(element, key)
            if isinstance(dictionary[key], dict):
                dict_to_elem(child, dictionary[key])
            else:
                child.text = str(dictionary[key])

    # Convert the dictionary to xml elements
    dict_to_elem(root, input_dict)

    # Create a string from the xml elements
    xml_string = tostring(root, 'utf-8')

    # Parse the xml string with minidom to pretty print the xml
    parsed_xml = parseString(xml_string)

    # Write the pretty printed xml to file
    with open(filename, 'w') as xml_file:
        xml_file.write(parsed_xml.toprettyxml(indent="  "))


def validate_xml_against_schema(xml_input: str | Path,
                                xsd_input: str | Path) -> None:
    xsd_tree = etree.parse(xsd_input)
    xsd_schema = etree.XMLSchema(xsd_tree)
    xml_tree = etree.parse(xml_input)
    try:
        xsd_schema.assertValid(xml_tree)
        print("# - The XML file is valid against the provided schema.")
    except etree.DocumentInvalid as e:
        print("# - The XML file is not valid "
              "against the schema. Error:", str(e))
