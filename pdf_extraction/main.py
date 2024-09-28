# import PyPDF2
# from .recommendations import extract_recommendations_from_pdf, parse_recommendation

# def extract_text_from_pdf(pdf_path, num_pages=3):
#     with open(pdf_path, 'rb') as file:
#         pdf_reader = PyPDF2.PdfReader(file)
#         text = ""
#         for page_num in range(min(num_pages, len(pdf_reader.pages))):
#             page = pdf_reader.pages[page_num]
#             text += page.extract_text()
#     return text

# # Usage
# pdf_path = '/home/shantanu/Downloads/CIS_Apple_macOS_14.0_Sonoma_Benchmark_v1.1.0.pdf'
# extracted_text = extract_text_from_pdf(pdf_path)
# print(extracted_text)

import json
from recommendations import extract_recommendations_from_pdf, parse_recommendation

pdf_path = '/home/shantanu/Desktop/BMC/docs/CIS_Microsoft_Windows_Server_2022_Benchmark_v3.0.0.pdf'
raw_recommendations = extract_recommendations_from_pdf(pdf_path, start_page=33, end_page=46)

parsed_recommendations = []
for raw_rec in raw_recommendations:
    print(raw_rec)
    try:
        parsed_rec = parse_recommendation(raw_rec)
        print("Parsed Recommendation: ", parsed_rec)
        parsed_recommendations.append(parsed_rec)
    except Exception as inst:
        print(type(inst))  
        print(inst.args)   
        print(inst)

recommendations_list = [recommendation.dict() for recommendation in parsed_recommendations]
with open("recommendations.json", "w") as json_file:
    json.dump(recommendations_list, json_file, indent=4)