import streamlit as st
import json
import os
from pdfTextExtraction import query, extract_header_index_from_pdf, remove_dots
from gemini import askLLM, get_prompt
from xmlTextExtraction import extract_data_from_xml,find_by_title
import xml.etree.ElementTree as ET  # Import ElementTree for XML parsing

def parse_file(file_type,file_bytes):
    if file_type == "application/pdf":
        header_list, index_list, key_list = extract_header_index_from_pdf(file_bytes)
        return header_list,index_list, key_list
    elif file_type == "text/xml":
        xml_content = file_bytes.decode("utf-8")
        header_list, index_list, key_list = extract_data_from_xml(xml_content)
        return header_list,index_list, key_list


# Function to load saved outputs from a JSON file
def load_saved_outputs():
    if os.path.exists('saved_outputs.json'):
        with open('saved_outputs.json', 'r') as f:
            return json.load(f)
    return []

# Function to save outputs to a JSON file
def save_outputs(outputs):
    with open('saved_outputs.json', 'w') as f:
        json.dump(outputs, f)

# Initialize session state for saved outputs
if 'saved_outputs' not in st.session_state:
    st.session_state.saved_outputs = load_saved_outputs()

# Sidebar for navigation
st.sidebar.title("Navigation")
view = st.sidebar.radio("Go to", ["Upload", "Saved Outputs"])

if view == "Upload":
    st.title("📝 Upload a file")
    uploaded_file = st.file_uploader("Upload a compliance standards document", type=("pdf", "xml"))
    
    compliance_standard = st.selectbox(
        "Which compliance standard is this?",
        ("CIS", "DISA"),
        disabled=not uploaded_file,
    )
    os = st.selectbox(
        "Which operating system is this compliance standard targeted at?",
        ("Ubuntu", "Windows", "macOS"),
        disabled=not uploaded_file,
    )

    if uploaded_file:
        file_bytes = uploaded_file.read()
        heading = None
        file_type = uploaded_file.type 
        header_list, index_list, key_list = parse_file(file_type,file_bytes)
    
        heading = st.selectbox("Select a heading", key_list)
        if compliance_standard == "CIS":
            confirm = st.button("Generate")
            if heading and confirm:
                try:
                    heading_doc = query(file_bytes, heading, index_list)
                    prompt = get_prompt(heading_doc, os)
                    response = askLLM(prompt)

                    # Save the output to session state and JSON file
                    new_output = {
                        'heading': heading,
                        'response': response
                    }
                    st.session_state.saved_outputs.append(new_output)
                    save_outputs(st.session_state.saved_outputs)

                    st.header("Response")
                    st.markdown(response)
                except TypeError as e:
                    st.error(f"Error: {e}")

        elif compliance_standard == "DISA":
            confirm = st.button("Generate")
            if heading and confirm:
                try:
                    heading_doc = find_by_title(index_list,heading)
                    prompt = get_prompt(heading_doc, os)
                    response = askLLM(prompt)

                    # Save the output to session state and JSON file
                    new_output = {
                        'heading': heading,
                        'response': response
                    }
                    st.session_state.saved_outputs.append(new_output)
                    save_outputs(st.session_state.saved_outputs)

                    st.header("Response")
                    st.markdown(response)
                except TypeError as e:
                    st.error(f"Error: {e}")

elif view == "Saved Outputs":
    st.title("📂 Saved Outputs")
    for i, output in enumerate(st.session_state.saved_outputs):
        st.subheader(f"Output {i + 1}")
        st.markdown(f"**Heading:** {output['heading']}")
        st.markdown(f"**Response:** \n {output['response']}")

    # Add a button to clear all saved outputs
    if st.button("Clear All Saved Outputs"):
        st.session_state.saved_outputs = []
        save_outputs([])
        st.success("All saved outputs have been cleared.")
        st.experimental_rerun()
