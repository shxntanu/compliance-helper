import streamlit as st
import json
import os
from pdfTextExtraction import query, extract_header_index_from_pdf, get_headings
from LLMScripts import *
from gemini import askLLM, get_prompt

def create_output_folder(issues_list, operating_system, model_id = "Qwen/Qwen2-72B-Instruct"):
    
    OUTPUT_FOLDER = "generated-scripts/"
    
    # Initialize a counter
    loop_counter = 0

    # Maximum iterations
    max_iterations = 5

    for json_data in issues_list:

        # Break the loop if it has run 10 times
        if loop_counter >= max_iterations:
            print(f"Reached maximum iteration limit ({max_iterations}). Exiting loop.")
            break

        # Increment the loop counter
        loop_counter += 1

        # If the input json_data is empty dont parse it
        if all_values_empty(json_data):
            st.write("Found empty JSON data. Skipping...")
            continue

        # Take out Title from the json_data
        title = json_data.get('Title', '')
        
        st.write(f"Processing: {title}")

        # Convert the python dict to string to pass to the model
        json_data = str(json_data)


        # Generate scripts using the JSON data
        try:
            if operating_system == "linux" or operating_system == "mac":
                audit_script, remediation_script = CIS_scripts_linux_mac(json_data, model_id = model_id)
                print("Successfully generated scripts from JSON data.")

            elif operating_system == "windows":
                audit_script, remediation_script = CIS_scripts_windows(json_data, model_id = model_id)
                print("Successfully generated scripts from JSON data.")

            else:
                print("Invalid operating system. Please choose 'linux', 'mac', or 'windows'.")
                return


        except Exception as e:
            print(f"Error generating scripts: {e}")
            return


        # Print the extracted scripts
        if audit_script:
            print("Extracted Audit Script:\n", audit_script)
        else:
            print("No Audit Script found.")

        if remediation_script:
            print("Extracted Remediation Script:\n", remediation_script)
        else:
            print("No Remediation Script found.")

        # Generate folder name
        folder_name = OUTPUT_FOLDER + name_of_the_folder(title)

        # Create folder if it doesn't exist
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        # Write the audit and remediation scripts to respective files
        audit_script_file = os.path.join(folder_name, "audit_script.sh")
        remediation_script_file = os.path.join(folder_name, "remediation_script.sh")

        if audit_script:
            with open(audit_script_file, 'w') as f:
                f.write(audit_script)
            st.write(f"Audit script written to {audit_script_file}")
        else:
            print("No audit script to write.")

        if remediation_script:
            with open(remediation_script_file, 'w') as f:
                f.write(remediation_script)
            st.write(f"Remediation script written to {remediation_script_file}")
        else:
            print("No remediation script to write.")

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
view = st.sidebar.radio("Go to", ["Upload", "Saved Outputs", "Fully Automate"])

if view == "Upload":
    st.title("📝 Upload a file")
    uploaded_file = st.file_uploader("Upload a compliance standards document", type=("pdf", "docx"))
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
        if uploaded_file.type == "application/pdf":
            file_bytes = uploaded_file.read()
            header_list, index_list, key_list = extract_header_index_from_pdf(file_bytes)
        else:
            st.error("Only PDF files are supported at the moment.")

        heading = st.selectbox("Select a heading", key_list)
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
        
        
        
elif view == "Fully Automate":
    st.title("🤖 Fully Automate")
    uploaded_file = st.file_uploader("Upload a compliance standards document", type=("pdf", "docx"))
    model = st.selectbox(
        "Select a model", 
        ["Qwen/Qwen2-72B-Instruct", "mistralai/Mixtral-8x22B-Instruct-v0.1", "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"], 
        disabled=not uploaded_file
    )
    operating_system = st.selectbox(
        "Which operating system is this compliance standard targeted at?",
        ("linux", "mac", "windows"),
        disabled=not uploaded_file,
    )
    
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            file_bytes = uploaded_file.read()
            header_list, index_list, key_list = extract_header_index_from_pdf(file_bytes)
            
            results = get_headings(file_bytes, key_list, index_list)
            
            st.subheader("Extracted Headings")
            st.json(results, expanded=2)
            
            if st.button("Create Scripts Folder"):
                with st.status("Creating scripts folder..."):
                    create_output_folder(results, operating_system, model)
        else:
            st.error("Only PDF files are supported at the moment.")