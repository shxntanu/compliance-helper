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

from recommendations import extract_recommendations_from_pdf, parse_recommendation

pdf_path = '/home/shantanu/Desktop/BMC/docs/CIS_Microsoft_Windows_Server_2022_Benchmark_v3.0.0.pdf'
raw_recommendations = extract_recommendations_from_pdf(pdf_path, start_page=34,)

parsed_recommendations = []
for raw_rec in raw_recommendations:
    try:
        parsed_rec = parse_recommendation(raw_rec)
        print("Parsed Recommendation: ", parsed_rec)
        parsed_recommendations.append(parsed_rec)
    except:
        continue

# Print the parsed recommendations
for i, rec in enumerate(parsed_recommendations, 1):
    print(f"Recommendation {i}:")
    print(f"Number: {rec.number}")
    print(f"Title: {rec.title}")
    print(f"Profile Applicability: {rec.profile_applicability}")
    print(f"Description: {rec.description[:100]}...")  # Truncated for brevity
    print("\n")