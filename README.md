![header](/assets/header.png)

> This project was made as a part of a hackathon that [BMC Software](https://www.bmc.com/) conducted at PICT Pune.

Creating compliance content is a very time consuming process due to the sheer length of the compliance documents and standards. This project aims to reduce the amount of manual work involved and makes creating audit and remediation scripts faster and easier.

## Our Team

-   [Charul Nampalliwar](https://github.com/charul2304)
-   [Piyush Agarwal](https://github.com/piyushhagarwal)
-   [Shantanu Wable](https://github.com/shxntanu)
-   [Sunay Bhoyar](https://github.com/sunaybhoyar)

## Problem Statement

> The detailed problem statement can be found [here](/assets/Hackathon%20Problem%20Statement%201.docx). This is a gist of it.

Compliance content development involves creating detection and remediation scripts, identifying and fixing rules, and automating script generation for diverse OS environments (e.g., PowerShell for Windows, shell scripts for Unix), based on guidelines from authorities like CIS, DISA, and PCI DSS, to ensure secure, compliant systems.

This process is time consuming due to its volume and complexity.

So, we need to find a workaround for all this manual effort and reduce the overall time required to study these documents at length, while still maintaining full compliance with their standards.

## Our Solution

![architecture](/assets/architecture.png)

<div align="center">

_Process Flow Diagram_

</div>

1. **User Uploads CIS/DISA Document**: The user uploads a CIS (Center for Internet Security) or DISA (Defense Information Systems Agency) compliance document (PDF or DOCX format) into the application.

2. **Application UI**: The user is prompted to upload the document using a simple drag-and-drop interface. The tool helps generate audit and remediation scripts based on the uploaded document.

3. **Document Parsing using Regex**: Once the document is uploaded, it is parsed using regular expressions (Regex) to extract important data, including headings and content sections.

4. **Structured Document**: The parsed document is structured into two main components:

    1. Index: A summary of key sections.
    2. Parsed Headings: The extracted headings from the document, which organize the content into a user-friendly format.

5. User Interaction with Parsed Headings: The user selects a heading of interest from the parsed headings.

6. Heading Data Fetch: Once a heading is selected, the relevant section's data is fetched.

7. LLM (Large Language Model) Integration: The LLM analyzes the fetched data and generates:

    1. A set of steps that can be displayed in the UI for user guidance.
    2. Scripts or commands that correspond to the compliance actions needed for the selected section.

8. Output Generation: The final output (steps, scripts, or audit information) is displayed in the application and saved for disk persistence.
