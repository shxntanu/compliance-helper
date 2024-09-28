import streamlit as st
from pdfTextExtraction import query, extract_header_index_from_pdf, remove_dots
from gemini import askLLM, get_prompt

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

# if uploaded_file and question and not anthropic_api_key:
#     st.info("Please add your Anthropic API key to continue.")

if uploaded_file:
    if uploaded_file.type == "application/pdf":
        header_list , index_list , key_list  = extract_header_index_from_pdf(uploaded_file)
        
        # This prints out the 3 lists
        st.write(header_list)
        st.write(index_list)
        st.write(key_list)
    else:
        st.error("Only PDF files are supported at the moment.")
        
    heading = st.selectbox("Select a heading", key_list)
    
    if heading:
        # Here it is giving error in the query function
        # Error: TypeError: 'int' object is not subscriptable
        heading_doc = query(uploaded_file, heading, index_list)
        
        prompt = get_prompt(heading_doc)
        
        response = askLLM(prompt)
        
        st.write(response)