import fitz 
import re 
pdf_path = 'CIS/macOS.pdf'

class HeaderDataNotFoundException(Exception):
    """Custom exception raised when header data is not found."""
    pass

def extract_header_from_pdf(page):
    CIS_header = {
        "OS": "",
        "Benchmark Name": "",
        "Version": "",
        "Issue Date": "",
    }
    
    text = page.get_text("text")
    lines = text.split('\n')

    try:
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
        
        if not CIS_header["OS"] or not CIS_header["Benchmark Name"] or not CIS_header["Version"] or not CIS_header["Issue Date"]:
            raise HeaderDataNotFoundException("Unable to find all required header data. The file might be incorrect or incomplete.")

        return CIS_header
    
    except Exception as e:
        print(f"Error: {e}")
        raise
    
def extract_titles_and_page_numbers(text):
    pattern = re.compile(r"(.+?)\s+\.{2,}\s*(\d+)\s*$")
    results = {} 
    
    lines = text.split('\n')
    
    for line in lines:
        match = pattern.match(line)
        if match:
            title = match.group(1).strip() 
            page_number = int(match.group(2)) 
            results[title] = page_number
    return results



def extract_data_from_pdf(pdf_path):
    pdf_document = fitz.open(pdf_path)
    data = []

    CIS_header = extract_header_from_pdf(pdf_document.load_page(0))

    CIS_index = {"Overview":-1}
    index_found_page = False 
    for page_no in range(1,pdf_document.page_count):
        text = pdf_document.load_page(page_no).get_text("text")
        if index_found_page and CIS_index["Overview"] == page_no :
            print(CIS_index)
            break 

        if 'Table of Contents' in text or index_found_page:
            CIS_index.update(extract_titles_and_page_numbers(text))
            index_found_page = True

    issue_data = {
        "Title of the Issue": "",
        "Profile Applicability": "",
        "Description": "",
        "Rationale": "",
        "Audit": "",
        "Remediation": "",
        "CIS Control": ""
    }

extracted_data = extract_data_from_pdf(pdf_path)
