import google.generativeai as genai
import os

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-1.5-flash")
# response = model.generate_content("Write a story about a magic backpack.")
# print(response.text)

"""
Let's say we have the following document that corresponds to a heading

{
    "Title": "1.1.2.1.4 Ensure noexec option set on /tmp partition (Automated)",
    "Profile Applicability": "\u2022  Level 1 - Server \n\u2022  Level 1 - Workstation",
    "Description": "The noexec mount option specifies that the filesystem cannot contain executable \nbinaries.",
    "Rationale": "Since the /tmp filesystem is only intended for temporary file storage, set this option to \nensure that users cannot run executable binaries from /tmp. \nImpact: \nSetting the noexec option on /tmp may prevent installation and/or updating of some 3rd \nparty software.",
    "Impact": "",
    "Audit": "- IF - a separate partition exists for /tmp, verify that the noexec option is set. \nRun the following command to verify that the noexec mount option is set. \nExample: \n# findmnt -kn /tmp | grep -v noexec \n \nNothing should be returned",
    "Remediation": "- IF - a separate partition exists for /tmp. \nEdit the /etc/fstab file and add noexec to the fourth field (mounting options) for the \n/tmp partition. \nExample: \n<device> /tmp    <fstype>     defaults,rw,nosuid,nodev,noexec,relatime  0 0 \nRun the following command to remount /tmp with the configured options: \n# mount -o remount /tmp",
    "References": "1. See the fstab(5) manual page for more information. \n2. NIST SP 800-53 Rev. 5: AC-3, MP-2",
    "Additional Information": "",
    "CIS Control": "Controls \nVersion \nControl \nIG 1 IG 2 IG 3 \nv8 \n3.3 Configure Data Access Control Lists \n \nConfigure data access control lists based on a user\u2019s need to know. Apply data \naccess control lists, also known as access permissions, to local and remote file \nsystems, databases, and applications. \n\u25cf \n\u25cf \n\u25cf \nv7 \n14.6 Protect Information through Access Control Lists \n \nProtect all information stored on systems with file system, network share, \nclaims, application, or database specific access control lists. These controls will \nenforce the principle that only authorized individuals should have access to the \ninformation based on their need to access the information as a part of their \nresponsibilities. \n\u25cf \n\u25cf \n\u25cf \n \nMITRE ATT&CK Mappings: \nTechniques / Sub-\ntechniques \nTactics \nMitigations \nT1204, T1204.002 \nTA0005 \nM1022"
},
"""

def get_prompt(heading_document: dict) -> str:
    prompt =f"""
    Objective: Generate a comprehensive BASH shell script which can be used for auditing, remediating and verifying the compliance standard for the following heading from a CIS/DISA Document:
    
    Title: {heading_document["Title"]}
    Profile Applicability: {heading_document["Profile Applicability"]}
    
    Description: {heading_document["Description"]}
    
    Rationale: {heading_document["Rationale"]}
    
    Impact: {heading_document["Impact"]}
    
    Audit: {heading_document["Audit"]}
    
    Remediation: {heading_document["Remediation"]}
    
    Additional Information: {heading_document["Additional Information"]}
    
    DO NOT HALLUCINATE.
    
    Only give the BASH shell script without any extra text.
    """
    
    return prompt

def askLLM(question: str) -> str:
    response = model.generate_content(question)
    return response.text
