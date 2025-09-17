import os

# --- Configuration ---
# The name of the file to be generated
output_filename = "PROJECT_CONTEXT.md"
# Directories to ignore
dirs_to_ignore = ['venv', '__pycache__', '.git', 'templates', 'recruitapp_core']
# Files to ignore
files_to_ignore = ['.env', 'db.sqlite3', 'debug.log', 'create_context.py']
# File extensions to include
extensions_to_include = ['.py', '.html', '.txt', 'Procfile']
# -------------------

def generate_context_file():
    """Walks the project directory and compiles the content of specified files into a single markdown file."""
    print(f"Generating {output_filename}...")

    with open(output_filename, 'w', encoding='utf-8') as outfile:
        outfile.write("# AxiomAgent Project Code Context\n\n")

        # First, write the directory structure
        outfile.write("## Project Structure\n\n")
        outfile.write("```\n")
        for root, dirs, files in os.walk("."):
            # Modify the dir list in place to exclude ignored directories
            dirs[:] = [d for d in dirs if d not in dirs_to_ignore]
            level = root.replace('.', '').count(os.sep)
            indent = ' ' * 4 * (level)
            outfile.write(f"{indent}{os.path.basename(root)}/\n")
            sub_indent = ' ' * 4 * (level + 1)
            for f in files:
                if not any(f.endswith(ext) for ext in extensions_to_include) or f in files_to_ignore:
                    continue
                outfile.write(f"{sub_indent}{f}\n")
        outfile.write("```\n\n")

        # Second, write the file contents
        outfile.write("## File Contents\n\n")
        for root, dirs, files in os.walk("."):
            # Modify the dir list in place to exclude ignored directories
            dirs[:] = [d for d in dirs if d not in dirs_to_ignore]
            for file in files:
                if not any(file.endswith(ext) for ext in extensions_to_include) or file in files_to_ignore:
                    continue

                file_path = os.path.join(root, file)
                outfile.write(f"--- \n\n")
                outfile.write(f"### File: `{file_path}`\n\n")
                outfile.write("```\n")
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        outfile.write(infile.read())
                except Exception as e:
                    outfile.write(f"Error reading file: {e}")
                outfile.write("\n```\n\n")

    print(f"Successfully created {output_filename}. You can now upload this file.")

if __name__ == "__main__":
    generate_context_file()