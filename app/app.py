import streamlit as st
import json
import os
from pdfTextExtraction import query, extract_header_index_from_pdf
from xmlTextExtraction import extract_data_from_xml, find_by_title
from LLMScripts import CIS_scripts_linux_mac, CIS_scripts_windows, all_values_empty, name_of_the_folder
from gemini import askLLM, get_prompt

@st.cache_data
def get_headings(file_bytes, key_list, index_list, file_type):
    if file_type == "application/pdf":
        results = []
        for key in key_list:
            result = query(file_bytes, key, index_list) 
            results.append(result)
            
        return results
    elif file_type == "text/xml":
        results = []
        for key in key_list:
            result = find_by_title(index_list, key)
            results.append(result)
            
        return results

def create_output_folder(issues_list, operating_system, model_id = "Qwen/Qwen2-72B-Instruct", compliance_standard= ""):
    
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
                audit_script, remediation_script = CIS_scripts_linux_mac(json_data, model_id = model_id, compliance_standard=compliance_standard)
                print("Successfully generated scripts from JSON data.")

            elif operating_system == "windows":
                audit_script, remediation_script = CIS_scripts_windows(json_data, model_id = model_id, compliance_standard=compliance_standard)
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

def generate_scripts_from_json(json_data, operating_system, model_id = "Qwen/Qwen2-72B-Instruct"):
    # Generate scripts using the JSON data
    try:
        if operating_system == "linux" or operating_system == "mac":
            st.write("🧠 Thinking...")
            audit_script, remediation_script = CIS_scripts_linux_mac(json_data, model_id = model_id)
            st.write("✅ Successfully generated scripts for the given heading.")

        elif operating_system == "windows":
            st.write("🧠 Thinking...")
            audit_script, remediation_script = CIS_scripts_windows(json_data, model_id = model_id)
            st.write("✅ Successfully generated scripts for the given heading.")

        else:
            print("Invalid operating system. Please choose 'linux', 'mac', or 'windows'.")
            return

    except Exception as e:
        st.error(f"Error generating scripts: {e}")
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

    return audit_script, remediation_script

def parse_file(file_type,file_bytes):
    if file_type == "application/pdf":
        header_list, index_list, key_list = extract_header_index_from_pdf(file_bytes)
        return header_list,index_list, key_list
    elif file_type == "text/xml":
        xml_content = file_bytes.decode("utf-8")
        header_list, index_list, key_list = extract_data_from_xml(xml_content)
        return header_list,index_list, key_list

# Function to load saved outputs from a JSON file
def load_saved_steps():
    if os.path.exists('saved_steps.json'):
        with open('saved_steps.json', 'r') as f:
            return json.load(f)
    return []

def load_saved_scripts():
    if os.path.exists('saved_scripts.json'):
        with open('saved_scripts.json', 'r') as f:
            return json.load(f)
    return []

# Function to save outputs to a JSON file
def save_steps(outputs):
    with open('saved_steps.json', 'w') as f:
        json.dump(outputs, f)
        
def save_scripts(outputs):
    with open('saved_scripts.json', 'w') as f:
        json.dump(outputs, f)

# Initialize session state for saved outputs
if 'saved_steps' not in st.session_state:
    st.session_state.saved_steps = load_saved_steps()
    
if 'saved_scripts' not in st.session_state:
    st.session_state.saved_scripts = load_saved_scripts()

# Sidebar for navigation
st.sidebar.title("Navigation")
view = st.sidebar.radio("Go to", ["Upload", "Saved Steps", "Saved Scripts"])

if view == "Upload":
    st.title("📝 Compliance - O - Matic")
    
    st.markdown("""
                This tool helps you generate **audit and remediation scripts** from compliance standards documents.
                Just upload a compliance standards document and select a **model** & **OS** to get started.
                """)
    
    st.subheader("Step 1.")
    uploaded_file = st.file_uploader("Upload a compliance standards document", type=("pdf", "XML"))
    
    st.subheader("Step 2.")
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
    
    compliance_standard = st.selectbox(
        "Which compliance standard is this?",
        ("CIS", "DISA"),
        disabled=not uploaded_file,
    )
    
    if uploaded_file:
        if uploaded_file.type == "application/pdf" or uploaded_file.type == "text/xml":
            file_bytes = uploaded_file.read()
            heading = None
            file_type = uploaded_file.type 
            header_list, index_list, key_list = parse_file(file_type,file_bytes)
            
            results = get_headings(file_bytes, key_list, index_list, file_type)
            
            st.subheader("Extracted Headings")
            st.json(results, expanded=2)
            
            st.subheader("")
            
            st.subheader("Step 3.")
            st.markdown("""
                Choose if you want to generate scripts for the extracted headings, or a set of steps from the selected heading.
                """)
            
            choice = st.selectbox("Select an Option", ["Scripts", "Set of Steps"])
            
            if choice == "Scripts":
                
                if st.selectbox("Select an option", ["All", "Selected"]) == "All":
                    if st.button("Generate Scripts"):
                        with st.status("Creating scripts folder..."):
                            create_output_folder(results, operating_system, model)
                    
                else:
                    heading = st.selectbox("Select a heading", key_list)
                    confirm = st.button("Generate")
                    
                    if heading and confirm:
                        try:
                            heading_doc = query(file_bytes, heading, index_list) if uploaded_file.type == "application/pdf" else find_by_title(index_list, heading)
                            with st.status("Generating scripts..."):
                                audit_script, remediation_script = generate_scripts_from_json(heading_doc, operating_system, model)
                                
                            new_output = {
                                'heading': heading,
                                'audit_script': audit_script,
                                'remediation_script': remediation_script
                            }
                                
                            st.session_state.saved_scripts.append(new_output)
                            save_scripts(st.session_state.saved_scripts)
                                
                            st.markdown(f"""
### Audit Script
```bash
{audit_script}
```

### Remediation Script
```bash
{remediation_script}
```""")
                            
                        except TypeError as e:
                            st.error(f"Error: {e}")
                        
            elif choice == "Set of Steps":
                heading = st.selectbox("Select a heading", key_list)
                confirm = st.button("Generate")
                
                if heading and confirm:
                    try:
                        heading_doc = query(file_bytes, heading, index_list) if uploaded_file.type == "application/pdf" else find_by_title(index_list, heading)
                        prompt = get_prompt(heading_doc, operating_system, compliance_standard)
                        response = askLLM(prompt)
                        
                        # Save the output to session state and JSON file
                        new_output = {
                            'heading': heading,
                            'response': response
                        }
                        st.session_state.saved_steps.append(new_output)
                        save_steps(st.session_state.saved_steps)
                        
                        st.subheader("Response")
                        st.markdown(response)
                    except TypeError as e:
                        st.error(f"Error: {
                            e
                        }")
        else:
            st.error("Only PDF files are supported at the moment.")

elif view == "Saved Steps":
    st.title("📂 Saved Steps")
    st.markdown("Here are the saved steps from previous runs.")
    
    for i, output in enumerate(st.session_state.saved_steps):
        st.subheader(f"Output {i + 1}")
        st.markdown(f"**Heading:** {output['heading']}")
        st.markdown(f"**Response:** \n {output['response']}")
        st.divider()

    # Add a button to clear all saved outputs
    if st.button("Clear All Saved Outputs"):
        st.session_state.saved_steps = []
        save_steps([])
        st.success("All saved outputs have been cleared.")
        st.experimental_rerun()
        
elif view == "Saved Scripts":
    st.title("📂 Saved Scripts")
    st.markdown("Here are the saved scripts from previous runs.")
    
    for i, output in enumerate(st.session_state.saved_scripts):
        st.subheader(f"Output {i + 1}")
        st.markdown(f"**Heading:** {output['heading']}")
        st.markdown(f"**Audit Script:** \n ```bash\n{output['audit_script']}\n```")
        st.markdown(f"**Audit Script:** \n ```bash\n{output['remediation_script']}\n```")
        st.divider()

    # Add a button to clear all saved outputs
    if st.button("Clear All Saved Outputs"):
        st.session_state.saved_scripts = []
        save_scripts([])
        st.success("All saved outputs have been cleared.")
        st.experimental_rerun()