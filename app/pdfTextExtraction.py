from PyPDF2 import PdfReader, PageObject
import re 
import streamlit as st
from streamlit.delta_generator import DeltaGenerator
import json


def remove_dots(text):
    # Use regex to remove dots and spaces from the end of the string
    cleaned_text = re.sub(r'[.\s]+$', '', text)
    return cleaned_text

class HeaderDataNotFoundException(Exception):
    """Custom exception raised when header data is not found."""
    pass

def extract_header_from_pdf(page: PageObject):
    # Dictionary to hold header information
    CIS_header = {
        "OS": "",
        "Benchmark Name": "",
        "Version": "",
        "Issue Date": "",
    }
    
    text = page.extract_text("text")
    lines = text.split('\n')

    try:
        # Extract relevant header data from the page text
        for i, line in enumerate(lines):
            if 'CIS' in line:
                CIS_header["OS"] = line[4:]
            elif 'Benchmark' in line:
                CIS_header["Benchmark Name"] = line
            elif len(line) > 0 and line[0] == 'v':
                split_line = line.split()
                if len(split_line) >= 3:
                    CIS_header["Version"] = split_line[0]
                    CIS_header["Issue Date"] = split_line[2]
                else:
                    raise ValueError("Version or Issue Date information is missing or malformed.")
        
        # Ensure all required header fields are present
        if not CIS_header["OS"] or not CIS_header["Benchmark Name"] or not CIS_header["Version"] or not CIS_header["Issue Date"]:
            raise HeaderDataNotFoundException("Unable to find all required header data. The file might be incorrect or incomplete.")

        return CIS_header
    
    except Exception as e:
        print(f"Error: {e}")
        raise

def extract_titles_and_page_numbers(text):
    # Regex pattern to extract title and page number
    pattern = re.compile(r"(.+?)\s+\.{2,}\s*(\d+)\s*$")
    results = {}
    lines = text.split('\n')

    merged_line = ""
    
    # Process each line, merging if necessary, and extract titles and page numbers
    for line in lines:
        if re.search(r"\d+\s*$", line):
            merged_line += " " + line.strip()
            match = pattern.match(merged_line)
            if match:
                title = match.group(1).strip()
                page_number = int(match.group(2))
                results[title] = page_number
            merged_line = ""
        else:
            merged_line += " " + line.strip()

    return results

def clean_internal_only_prefix(data_dict):
    # Clean up "Internal Only - General" prefix from dictionary keys
    cleaned_dict = {}
    
    for key, value in data_dict.items():
        if key.startswith("Internal Only - General"):
            cleaned_key = key.replace("Internal Only - General ", "").strip()
        else:
            cleaned_key = key
        cleaned_dict[cleaned_key] = value
    
    return cleaned_dict

def calculate_page_ranges(page_dict):
    # Calculate page ranges for titles based on page numbers
    sorted_items = sorted(page_dict.items(), key=lambda x: x[1])
    page_ranges = {}

    # Assign page ranges based on subsequent start pages
    for i in range(len(sorted_items)):
        title, start_page = sorted_items[i]
        
        if i < len(sorted_items) - 1:
            next_start_page = sorted_items[i + 1][1]
            end_page = next_start_page - 1
        else:
            end_page = start_page
    
        page_ranges[title] = [start_page, end_page]
    
    return page_ranges

@st.cache_data
def extract_header_index_from_pdf(pdf_path):
    # Open the PDF document
    reader = PdfReader(pdf_path)

    # Extract header from the first page
    CIS_header = extract_header_from_pdf(reader.pages[0])

    # Initialize the index and tracking variables
    CIS_index = {"Overview":-1}
    index_found_page = False
    
    # Loop through the PDF pages to extract the index
    for page_num in range(1, len(reader.pages)):
        page = reader.pages[page_num]
        text = page.extract_text()
        
        # Clean and calculate ranges once the "Overview" page number is found
        if index_found_page and CIS_index["Overview"] == page_num:
            CIS_index = clean_internal_only_prefix(CIS_index)
            CIS_index = calculate_page_ranges(CIS_index)
            break  # Stop processing further pages

        # Start extracting index after finding the "Table of Contents"
        if 'Table of Contents' in text or index_found_page:
            CIS_index.update(extract_titles_and_page_numbers(text))
            index_found_page = True

        # Find the first title starting with "1" (start of compliance)
        keys_list = list(CIS_index.keys())
        start_of_compalience = -1
        for index, key in enumerate(keys_list):
            if key.startswith("1"):
                start_of_compalience = index
                break
    
    # Extract keys after the start of compliance
    key_list = keys_list[start_of_compalience:]

    return CIS_header, CIS_index, key_list

def query(pdf_path, given_query, index_list):
    # Open the PDF document
    reader = PdfReader(pdf_path)
    page_range = index_list[given_query]
    text = ""
    for page_num in range(page_range[0],page_range[1]+1):
        text += reader.pages[page_num].extract_text()

    data = {
        "Title": "",
        "Profile Applicability": "",
        "Description": "",
        "Rationale": "",
        "Impact": "",
        "Audit": "",
        "Remediation": "",
        "References": "",
        "Additional Information": "",
        "CIS Control": ""
    }

    # Regex patterns for each section
    sections = {
        "Title": r"^(.*?)\n(?=Profile Applicability|Description|Rationale|Audit|Remediation|References|CIS Controls)",
        "Profile Applicability": r"Profile Applicability:\s*(.*?)\n(?=Description|Rationale|Audit|Remediation|References|CIS Controls|$)",
        "Description": r"Description:\s*(.*?)\n(?=Rationale|Audit|Remediation|References|CIS Controls|$)",
        "Rationale": r"Rationale:\s*(.*?)\n(?=Audit|Remediation|References|CIS Controls|$)",
        "Audit": r"Audit:\s*(.*?)\n(?=Remediation|References|CIS Controls|$)",
        "Remediation": r"Remediation:\s*(.*?)\n(?=References|CIS Controls|$)",
        "References": r"References:\s*(.*?)\n(?=CIS Controls|$)",
        "CIS Control": r"CIS Controls:\s*(.*?)$"
    }

    # Remove page numbers and unwanted text
    text = re.sub(r"Page \d+", "", text)

    # Extract each section using regex
    for section, pattern in sections.items():
        match = re.search(pattern, text, re.DOTALL)  # DOTALL makes '.' match newlines too
        if match:
            data[section] = match.group(1).strip() 
    
    return data 

# header_list , index_list , key_list  = extract_header_index_from_pdf()
# for keyl in key_list:
#     print(keyl)
# results = []
# for key in key_list:
#     result = query(key) 
#     results.append(result) 

# # Write the results to a JSON file
# with open('output/'+file_name+'.json', 'w') as json_file:
#     json.dump(results, json_file, indent=4) 

# print("Data has been written to "+file_name+".json")