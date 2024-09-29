import os
import subprocess

def run_script(script_path):
    """Function to run a shell script and return the output and exit status."""
    try:
        # Run the script
        result = subprocess.run(['bash', script_path], capture_output=True, text=True)
        return result.stdout, result.returncode
    except Exception as e:
        print(f"Error running {script_path}: {e}")
        return None, -1

def explore_and_run_scripts(folder_path):
    """Recursively explore folders and run audit and remediation scripts."""
    # Walk through the directory tree
    for root, dirs, files in os.walk(folder_path):
        # Check if both audit_script.sh and remediation_script.sh are present
        if 'audit_script.sh' in files and 'remediation_script.sh' in files:
            audit_script_path = os.path.join(root, 'audit_script.sh')
            remediation_script_path = os.path.join(root, 'remediation_script.sh')

            # Run the audit script
            print(f"\nRunning audit script: {audit_script_path}")
            audit_output, audit_status = run_script(audit_script_path)

            if audit_status == 0:
                print(f"Audit script PASSED:\n{audit_output}")
                
                # If audit passes, run the remediation script
                print(f"Running remediation script: {remediation_script_path}")
                remediation_output, remediation_status = run_script(remediation_script_path)
                
                if remediation_status == 0:
                    print(f"Remediation script PASSED:\n{remediation_output}")
                else:
                    print(f"Remediation script FAILED with exit code {remediation_status}:\n{remediation_output}")
            else:
                print(f"Audit script FAILED with exit code {audit_status}:\n{audit_output}")

if __name__ == "__main__":
    # Define the path to the main folder
    folder_to_explore = "/path/to/main/folder"
    
    # Explore the folder and run the scripts
    explore_and_run_scripts(folder_to_explore)
