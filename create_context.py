import os

# --- Configuration ---
# The name of the file to be generated
output_filename = "PROJECT_CONTEXT.md"

# Directories to ignore. 'recruitapp_core' and 'templates' have been REMOVED from this list.
# 'staticfiles' has been ADDED as it's a generated directory.
dirs_to_ignore = ['venv', '__pycache__', '.git', 'staticfiles']

# Files to ignore (e.g., secrets, databases, logs)
files_to_ignore = ['.env', 'db.sqlite3', 'debug.log', 'create_context.py', 'PROJECT_CONTEXT.md']

# File extensions to include in the context
extensions_to_include = ['.py', '.html', '.txt', 'Procfile', '.css']
# -------------------

def generate_context_file():
    """Walks the project directory and compiles the content of specified files into a single markdown file."""
    print(f"Generating {output_filename}...")

    with open(output_filename, 'w', encoding='utf-8') as outfile:
        outfile.write("# RecruitApp Project Code Context\n\n")

        # First, write the complete directory structure
        outfile.write("## Project Structure\n\n")
        outfile.write("```\n")
        # Use a list to hold structure lines to sort them later for consistency
        structure_lines = []
        for root, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if d not in dirs_to_ignore]
            
            # Sort dirs and files to ensure a consistent order every time the script is run
            dirs.sort()
            files.sort()

            level = root.replace('.', '').count(os.sep)
            indent = ' ' * 4 * (level)
            
            # Add the directory to the list
            structure_lines.append(f"{indent}{os.path.basename(root)}/\n")
            
            sub_indent = ' ' * 4 * (level + 1)
            for f in files:
                # Check against ignored files and included extensions
                if f in files_to_ignore or not any(f.endswith(ext) for ext in extensions_to_include):
                    continue
                structure_lines.append(f"{sub_indent}{f}\n")
        
        outfile.writelines(structure_lines)
        outfile.write("```\n\n")

        # Second, write the file contents
        outfile.write("## File Contents\n\n")
        for root, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if d not in dirs_to_ignore]
            
            # Sort files for consistent output
            files.sort()

            for file in files:
                if file in files_to_ignore or not any(file.endswith(ext) for ext in extensions_to_include):
                    continue

                file_path = os.path.join(root, file).replace('\\', '/') # Standardize path separators
                outfile.write(f"---\n\n")
                outfile.write(f"### File: `./{file_path}`\n\n")
                
                # Determine language for syntax highlighting based on extension
                lang = file.split('.')[-1]
                if lang == 'py': lang = 'python'
                if lang == 'html': lang = 'html'
                if lang == 'css': lang = 'css'
                
                outfile.write(f"```{lang}\n")
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        outfile.write(infile.read())
                except Exception as e:
                    outfile.write(f"Error reading file: {e}")
                outfile.write("\n```\n\n")

    print(f"Successfully created {output_filename}. You can now upload this file.")

if __name__ == "__main__":
    generate_context_file()