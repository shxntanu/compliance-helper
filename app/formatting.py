import re

def format_shell_code(shell_code):
    # Add newlines after certain keywords and closing brackets
    shell_code = re.sub(r';', ';\n', shell_code)  # Add newline after semicolons
    shell_code = re.sub(r'\{', '{\n', shell_code)  # Add newline after opening braces
    shell_code = re.sub(r'\}', '}\n', shell_code)  # Add newline after closing braces

    # Add newlines after `if`, `else`, `fi`, `for`, `do`, `done`
    shell_code = re.sub(r'\b(if|else|fi|for|do|done|then|elif)\b', r'\1\n', shell_code)

    # Format for proper indentation
    indent_level = 0
    formatted_code = []
    
    for line in shell_code.splitlines():
        line = line.strip()

        if line.endswith("}") or line == "fi" or line == "done":  # Decrease indent after closing brace or end of block
            indent_level -= 1

        formatted_code.append("    " * indent_level + line)

        if line.endswith("{") or line.startswith("if") or line.startswith("for") or line == "do":  # Increase indent after block start
            indent_level += 1

    return '\n'.join(formatted_code)