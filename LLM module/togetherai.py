

# pip install together

import os
from together import Together

# Initialize the API client with your Together API key
client = Together(api_key='')

# Function to generate audit and remediation scripts from compliance JSON data for mac and linux
def CIS_scripts_linux_mac(json_data, model_id="Qwen/Qwen2-72B-Instruct", max_tokens=4000, temperature=0.0):
    """
    This function takes a JSON input and generates audit and remediation scripts in bash
    based on the provided compliance rules. It uses Together's LLM API to process the input
    and return the desired scripts.

    :param json_data: A JSON string containing compliance  information.
    :param model_id: The ID of the language model to use for generating the scripts.
    :param max_tokens: The maximum number of tokens for the model to generate.
    :param temperature: Controls randomness in output (0.1 = deterministic, lower randomness).
    :return: A string containing both the audit and remediation scripts.
    """

    # Define the prompt to be sent to the model
    prompt = f"""
      You are tasked with automating the generation of audit and remediation scripts in bash based on compliance rules provided in JSON format.
      The JSON input will include fields such as the compliance title, description, audit instructions, remediation steps, and references. Based on this structured data, you need to:
      1. Generate an Audit Script:
        - The script should verify whether the system meets the compliance requirements.
        - Print PASS if the system complies, or FAIL with specific reasons if it doesn't.

      2. Generate a Remediation Script:
        - The remediation script should apply necessary fixes based on the remediation instructions provided in the JSON.

      The input json: {json_data}

      Format of the output:

      # Audit Script
      ```bash

      ```

      --------------------

      # Remediation Script
      ```bash

      ```

      The output should be in above format only.
    """

    # Make the API request to generate the response
    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=max_tokens,
        temperature=temperature,
    )

    # Extract the generated output from the response
    output = response.choices[0].message.content
    return output


# Function to generate audit and remediation scripts from compliance JSON data for windows
def CIS_scripts_windows(json_data, model_id="Qwen/Qwen2-72B-Instruct", max_tokens=4000, temperature=0.0):
    """
    This function takes a JSON input and generates audit and remediation scripts in powershell
    based on the provided compliance rules. It uses Together's LLM API to process the input
    and return the desired scripts.

    :param json_data: A JSON string containing compliance  information.
    :param model_id: The ID of the language model to use for generating the scripts.
    :param max_tokens: The maximum number of tokens for the model to generate.
    :param temperature: Controls randomness in output (0.1 = deterministic, lower randomness).
    :return: A string containing both the audit and remediation scripts.
    """

    # Define the prompt to be sent to the model
    prompt = f"""
      You are tasked with automating the generation of audit and remediation scripts in powershell based on compliance rules provided in JSON format.
      The JSON input will include fields such as the compliance title, description, audit instructions, remediation steps, and references. Based on this structured data, you need to:
      1. Generate an Audit Script:
        - The script should verify whether the system meets the compliance requirements.
        - Print PASS if the system complies, or FAIL with specific reasons if it doesn't.

      2. Generate a Remediation Script:
        - The remediation script should apply necessary fixes based on the remediation instructions provided in the JSON.

      The input json: {json_data}

      Format of the output:

      # Audit Script
      ```powershell

      ```

      --------------------

      # Remediation Script
      ```powershell

      ```

      The output should be in above format only.
    """

    # Make the API request to generate the response
    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=max_tokens,
        temperature=temperature,
    )

    # Extract the generated output from the response
    output = response.choices[0].message.content
    return output

import re

def extract_scripts_linux_mac(text):
    """
    Extracts audit and remediation scripts from a given text.

    Args:
        text (str): The input text containing audit and remediation scripts.

    Returns:
        tuple: A tuple containing two elements:
            - audit (str or None): The extracted audit script if found, otherwise None.
            - remediation (str or None): The extracted remediation script if found, otherwise None.
    """

    # Define regex patterns to match the audit and remediation script blocks
    # The patterns look for '### Audit Script' and '### Remediation Script' followed by a code block in bash
    audit_pattern = r'# Audit Script\s+```bash(.*?)```'
    remediation_pattern = r'# Remediation Script\s+```bash(.*?)```'

    # Use re.DOTALL to allow '.' to match newline characters, enabling multiline captures
    audit_script = re.search(audit_pattern, text, re.DOTALL)
    remediation_script = re.search(remediation_pattern, text, re.DOTALL)

    # Extract the script content if the search found a match
    # Use .group(1) to get the content within the first capturing group
    audit = audit_script.group(1).strip() if audit_script else None  # Strip leading/trailing whitespace
    remediation = remediation_script.group(1).strip() if remediation_script else None  # Strip leading/trailing whitespace

    # Return the extracted audit and remediation scripts as a tuple
    return audit, remediation


def extract_scripts_windows(text):
    """
    Extracts audit and remediation scripts from a given text.

    Args:
        text (str): The input text containing audit and remediation scripts.

    Returns:
        tuple: A tuple containing two elements:
            - audit (str or None): The extracted audit script if found, otherwise None.
            - remediation (str or None): The extracted remediation script if found, otherwise None.
    """

    # Define regex patterns to match the audit and remediation script blocks
    # The patterns look for '### Audit Script' and '### Remediation Script' followed by a code block in bash
    audit_pattern = r'# Audit Script\s+```powershell(.*?)```'
    remediation_pattern = r'# Remediation Script\s+```powershell(.*?)```'

    # Use re.DOTALL to allow '.' to match newline characters, enabling multiline captures
    audit_script = re.search(audit_pattern, text, re.DOTALL)
    remediation_script = re.search(remediation_pattern, text, re.DOTALL)

    # Extract the script content if the search found a match
    # Use .group(1) to get the content within the first capturing group
    audit = audit_script.group(1).strip() if audit_script else None  # Strip leading/trailing whitespace
    remediation = remediation_script.group(1).strip() if remediation_script else None  # Strip leading/trailing whitespace

    # Return the extracted audit and remediation scripts as a tuple
    return audit, remediation

# Helper functions

import re
import json

def name_of_the_folder(text):
    # Extract the first word
    first_word = text.split()[0]
    # Replace dots with slashes
    modified_word = first_word.replace('.', '/')
    return modified_word

def extract_title_from_json_string(json_string):
    # Regular expression to capture the value corresponding to the "Title" key
    match = re.search(r'"Title"\s*:\s*"([^"]*)"', json_string)
    if match:
        return match.group(1)
    else:
        return None

def json_to_array(file_path):
    """
    Reads a JSON file containing an array and returns it as a Python list.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        list: A Python list representation of the JSON array.

    Raises:
        ValueError: If the JSON data is not an array.
        FileNotFoundError: If the file is not found at the given path.
        json.JSONDecodeError: If the JSON data cannot be decoded.
    """
    try:
        # Open and read the JSON file
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Check if the JSON data is an array
        if not isinstance(data, list):
            raise ValueError("The JSON data is not an array.")

        return data

    except FileNotFoundError:
        print(f"Error: File not found at path {file_path}")
        raise
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON.")
        raise
    except ValueError as ve:
        print(f"Error: {ve}")
        raise


def all_values_empty(input_dict):
    """
    Checks if all values in the given dictionary are empty.

    Args:
        input_dict (dict): The dictionary to check.

    Returns:
        bool: True if all values in the dictionary are empty, False otherwise.
    """
    for value in input_dict.values():
        # Check if the value is empty (covers '', None, [], {}, etc.)
        if value:  # Will evaluate as False for empty values like '', None, [], {}, 0, False
            return False
    return True

import os
import json

def create_output_folder(json_file_path, operating_system, model_id = "Qwen/Qwen2-72B-Instruct"):

    # Load the JSON file into python list
    issues_list = json_to_array(json_file_path)

    # Initialize a counter
    loop_counter = 0

    # Maximum iterations
    max_iterations = 10

    for json_data in issues_list:


        # Break the loop if it has run 10 times
        if loop_counter >= max_iterations:
            print("Reached maximum iteration limit (10). Exiting loop.")
            break

        # Increment the loop counter
        loop_counter += 1

        # If the input json_data is empty dont parse it
        if all_values_empty(json_data):
            continue

        # Take out Title from the json_data
        title = json_data.get('Title', '')

        # Convert the python dict to string to pass to the model
        json_data = str(json_data)


        # Generate scripts using the JSON data
        try:
            if operating_system == "linux" or operating_system == "mac":
                generated_scripts = CIS_scripts_linux_mac(json_data, model_id = model_id)
                print("Successfully generated scripts from JSON data.")

                # Extract audit and remediation scripts
                audit_script, remediation_script = extract_scripts_linux_mac(generated_scripts)

                max_attempts = 3

                while (not audit_script or not remediation_script) and max_attempts != 0:
                    print(f"Attempting to regenerate scripts. Attempts left: {max_attempts}")

                    # Generate scripts using the JSON data
                    try:
                        generated_scripts = CIS_scripts_linux_mac(json_data, model_id = model_id)
                        print("Successfully generated scripts from JSON data.")
                    except Exception as e:
                        print(f"Error generating scripts: {e}")
                        return

                    audit_script, remediation_script = extract_scripts_linux_mac(generated_scripts)
                    max_attempts -= 1

                    print(generated_scripts)

            elif operating_system == "windows":
                generated_scripts = CIS_scripts_windows(json_data, model_id = model_id)
                print("Successfully generated scripts from JSON data.")

                # Extract audit and remediation scripts
                audit_script, remediation_script = extract_scripts_windows(generated_scripts)

                max_attempts = 3

                while (not audit_script or not remediation_script) and max_attempts != 0:
                    print(f"Attempting to regenerate scripts. Attempts left: {max_attempts}")

                    # Generate scripts using the JSON data
                    try:
                        generated_scripts = CIS_scripts_windows(json_data, model_id = model_id)
                        print("Successfully generated scripts from JSON data.")
                    except Exception as e:
                        print(f"Error generating scripts: {e}")
                        return

                    audit_script, remediation_script = extract_scripts_windows(generated_scripts)
                    max_attempts -= 1

                    print(generated_scripts)

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
        folder_name = name_of_the_folder(title)

        # Create folder if it doesn't exist
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        # Write the audit and remediation scripts to respective files
        audit_script_file = os.path.join(folder_name, "audit_script.sh")
        remediation_script_file = os.path.join(folder_name, "remediation_script.sh")

        if audit_script:
            with open(audit_script_file, 'w') as f:
                f.write(audit_script)
            print(f"Audit script written to {audit_script_file}")
        else:
            print("No audit script to write.")

        if remediation_script:
            with open(remediation_script_file, 'w') as f:
                f.write(remediation_script)
            print(f"Remediation script written to {remediation_script_file}")
        else:
            print("No remediation script to write.")


create_output_folder("/content/ubuntu.json", "linux")


