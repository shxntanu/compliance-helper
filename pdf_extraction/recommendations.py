from pydantic import BaseModel, Field
from typing import List, Optional
import re
from PyPDF2 import PdfReader

class Recommendation(BaseModel):
    number: Optional[str] = Field(default="")
    title: Optional[str] = Field(default="")
    profile_applicability: List[str] = Field(default_factory=list)
    description: Optional[str] = Field(default="")
    rationale: Optional[str] = Field(default="")
    impact: Optional[str] = Field(default="")
    audit: List[str] = Field(default_factory=list)
    remediation: List[str] = Field(default_factory=list)
    default_value: Optional[str] = Field(default="")
    references: List[str] = Field(default_factory=list)
    additional_information: Optional[str] = Field(default="")
    cis_controls: List[dict] = Field(default_factory=list)

    def __str__(self) -> str:
        return (
            f"Number: {self.number}\n\n"
            f"Title: {self.title}\n\n"
            f"Profile Applicability: {self.profile_applicability}\n\n"
            f"Description: {self.description}\n\n"
            f"Rationale: {self.rationale}\n\n"
            f"Impact: {self.impact}\n\n"
            f"Audit: {self.audit}\n\n"
            f"Remediation: {self.remediation}\n\n"
            f"Default Value: {self.default_value}\n\n"
            f"References: {self.references}\n\n"
            f"Additional Information: {self.additional_information}\n\n"
            f"CIS Controls: {self.cis_controls}\n"
        )
        
def extract_recommendations_from_pdf(pdf_path, end_page=None, start_page=18):
    reader = PdfReader(pdf_path)
    recommendations = []
    current_recommendation = ""
    
    for page_num in range(start_page, len(reader.pages) if end_page == None else end_page):
        page = reader.pages[page_num]
        text = page.extract_text()
        
        # Remove page numbers from the text
        text = re.sub(r'Page \d+ ', '', text)
        
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

def parse_recommendation(text: str) -> Recommendation:
    text = text.strip()
    
    # Extract number and title
    print("Text: ", text)
    match = re.match(r'(\d+(?:\.\d+)+)\s+(.+)', text.split('\n')[0])
    print("Match Grps: ", match.groups())
    number, title = match.groups() if match else ("", "")

    # Extract other sections
    sections = re.split(r'\n(?=Profile Applicability:|Description:|Rationale:|Impact:|Audit:|Remediation:|Default Value:|References:|Additional Information:|CIS Controls:)', text)
    data = {
        'number': number,
        'title': title,
        'profile_applicability': [],
        'description': "",
        'rationale': "",
        'impact': "",
        'audit': [],
        'remediation': [],
        'default_value': "",
        'references': [],
        'additional_information': "",
    }

    for section in sections[1:]:  # Skip the first section (title)
        if section.startswith('Profile Applicability:'):
            data['profile_applicability'] = [level.strip() for level in section.split('\n')[1:] if level.strip()]
        elif section.startswith('Description:'):
            data['description'] = '\n'.join(section.split('\n')[1:]).strip()
        elif section.startswith('Rationale:'):
            data['rationale'] = '\n'.join(section.split('\n')[1:]).strip()
        elif section.startswith('Impact:'):
            data['impact'] = '\n'.join(section.split('\n')[1:]).strip()
        elif section.startswith('Audit:'):
            data['audit'] = [audit.strip() for audit in section.split('\n')[1:] if audit.strip()]
        elif section.startswith('Remediation:'):
            data['remediation'] = [rem.strip() for rem in section.split('\n')[1:] if rem.strip()]
        elif section.startswith('Default Value:'):
            data['default_value'] = '\n'.join(section.split('\n')[1:]).strip()
        elif section.startswith('References:'):
            data['references'] = [ref.strip() for ref in section.split('\n')[1:] if ref.strip()]
        elif section.startswith('Additional Information:'):
            data['additional_information'] = '\n'.join(section.split('\n')[1:]).strip()

    return Recommendation(**data)