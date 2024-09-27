import re
from PyPDF2 import PdfReader

def extract_recommendations_from_pdf(pdf_path, end_page, start_page=18):
    reader = PdfReader(pdf_path)
    recommendations = []
    current_recommendation = ""
    
    for page_num in range(start_page, len(reader.pages) if end_page == None else end_page):
        page = reader.pages[page_num]
        text = page.extract_text()
        
        # Check if this page starts a new recommendation
        if re.match(r'^\d+\.\d+\s+', text.strip()):
            if current_recommendation:
                recommendations.append(current_recommendation)
            current_recommendation = text
        else:
            current_recommendation += "\n" + text
    
    # Add the last recommendation
    if current_recommendation:
        recommendations.append(current_recommendation)
    
    return recommendations

class Recommendation:
    def __init__(self):
        self.number = ""
        self.title = ""
        self.profile_applicability = []
        self.description = ""
        self.rationale = ""
        self.impact = ""
        self.audit = ""
        self.remediation = ""
        self.default_value = ""
        self.references = []
        self.additional_information = ""
        self.cis_controls = []

    def __str__(self) -> str:
        return f"Number: {self.number}\nTitle: {self.title}\nProfile Applicability: {self.profile_applicability}\nDescription: {self.description[:100]}\nRationale: {self.rationale[:100]}\nImpact: {self.impact[:100]}\nAudit: {self.audit}\nRemediation: {self.remediation}\nDefault Value: {self.default_value}\nReferences: {self.references}\nAdditional Information: {self.additional_information[:100]}\nCIS Controls: {self.cis_controls}"

def parse_recommendation(text):
    rec = Recommendation()
    
    # Extract number and title
    match = re.match(r'(\d+\.\d+)\s+(.+)', text.split('\n')[0])
    if match:
        rec.number, rec.title = match.groups()
    
    # Extract other sections
    sections = re.split(r'\n(?=Profile Applicability:|Description:|Rationale:|Impact:|Audit:|Remediation:|Default Value:|References:|Additional Information:|CIS Controls:)', text)
    
    for section in sections[1:]:  # Skip the first section (title)
        if section.startswith('Profile Applicability:'):
            rec.profile_applicability = [level.strip() for level in section.split('\n')[1:] if level.strip()]
        elif section.startswith('Description:'):
            rec.description = '\n'.join(section.split('\n')[1:]).strip()
        elif section.startswith('Rationale:'):
            rec.rationale = '\n'.join(section.split('\n')[1:]).strip()
        elif section.startswith('Impact:'):
            rec.impact = '\n'.join(section.split('\n')[1:]).strip()
        elif section.startswith('Audit:'):
            rec.audit = [audit.strip() for audit in section.split('\n')[1:] if audit.strip()]
        elif section.startswith('Remediation:'):
            rec.remediation = [rem.strip() for rem in section.split('\n')[1:] if rem.strip()]
        elif section.startswith('Default Value:'):
            rec.default_value = [def_val.strip() for def_val in section.split('\n')[1:] if def_val.strip()]
        elif section.startswith('References:'):
            rec.references = [ref.strip() for ref in section.split('\n')[1:] if ref.strip()]
        elif section.startswith('Additional Information:'):
            rec.additional_information = '\n'.join(section.split('\n')[1:]).strip()
        elif section.startswith('CIS Controls:'):
            # controls_lines = section.split('\n')[1:]
            # for line in controls_lines:
            #     if line.strip():
            #         version, control = line.split(':', 1)
            #         rec.cis_controls.append({
            #             'version': version.strip(),
            #             'control': control.strip()
            #         })
            pass # Skip this section for now as we need to read tables
    
    return rec