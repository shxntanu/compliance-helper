import copy
import xml.etree.ElementTree as ET
import json
import re
import streamlit as st

header = {
        "OS": "",
        "Benchmark Name": "",
        "Version": "",
        "Issue Date": "",
    }

empty_section = {
        "Title": "",
        "Profile Applicability":"",
        "Description":"",
        "Rationale":"",
        "Audit":"",
        "Remediation":"",
        "References":"",
        "CIS Control": ""  
        }

data = []


def strip_namespace(tag):
    """Removes the namespace from the XML tag."""
    if '}' in tag:
        return tag.split('}', 1)[1]  # Split the tag to remove the namespace
    return tag

def xml_to_json(xml_content):
    root = ET.fromstring(xml_content)

    def parse_element(element):
        parsed_data = {}
        # Process attributes if they exist
        if element.attrib:
            parsed_data.update({"@attributes": element.attrib})

        # Iterate over child elements
        for child in element:
            child_data = parse_element(child)
            child_tag = strip_namespace(child.tag)  # Strip namespace from the tag

            # Handle duplicate child names
            if child_tag in parsed_data:
                if isinstance(parsed_data[child_tag], list):
                    parsed_data[child_tag].append(child_data)
                else:
                    parsed_data[child_tag] = [parsed_data[child_tag], child_data]
            else:
                parsed_data[child_tag] = child_data

        # Add text content if it exists
        if element.text and element.text.strip():
            parsed_data = element.text.strip()

        return parsed_data

    # Create a root dictionary, stripping the namespace from the root tag
    json_data = {strip_namespace(root.tag): parse_element(root)}

    # Convert the dictionary to JSON
    json_output = json.dumps(json_data, indent=4)
    
    return json_output

@st.cache_data
def extract_data_from_xml(xml_content):
    try:
        json_output = xml_to_json(xml_content)
        jsondata = json.loads(json_output)['Benchmark']
        header["OS"] = jsondata['title']
        header["Benchmark Name"] =   jsondata['title']
        match = re.search(r'\d{2} \w+ \d{4}', jsondata["plain-text"][0])
        if match:
            header["Issue Date"]  = match.group(0) 
        header["Version"] = jsondata["plain-text"][2]
        groups = jsondata["Group"]

        key_list = []

        for group in range(len(groups)):
            rule = groups[group]["Rule"]
            
            # Create a new copy of empty_section for each iteration
            section = copy.deepcopy(empty_section)
            
            section["Title"] = str(group + 1) + " " + rule["title"]
            key_list.append(section["Title"])
            section["Description"] = rule["description"]
            section["Audit"] = rule["check"]["check-content"]
            section["Remediation"] = rule["fixtext"]
            
            data.append(section)
        return header,data,key_list
    

    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return json.dumps({"error": "Invalid XML format"})
    except Exception as e:
        print(f"Unexpected error: {e}")
        return json.dumps({"error": str(e)})
    

def find_by_title(data, title_text):
    for section in data:
        if section["Title"] == title_text:
            return section
    return None  
