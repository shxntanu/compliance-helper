import PyPDF2

def extract_text_from_pdf(pdf_path, num_pages=3):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page_num in range(min(num_pages, len(pdf_reader.pages))):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    return text

# Usage
pdf_path = 'path/to/your/CIS_MacOS_Sonoma_Benchmark.pdf'
extracted_text = extract_text_from_pdf(pdf_path)
print(extracted_text)