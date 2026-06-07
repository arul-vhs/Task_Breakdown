import os

def aggregate_files(root_dir, output_file):
    excluded_dirs = {'.git', '__pycache__', 'env', '.gemini'}
    excluded_files = {'.gitignore', '.state_cache.json', 'project_codebase_dump.txt', 'test.txt'}
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write("========================================= \n")
        outfile.write("PROJECT CODEBASE SUMMARY AND SOURCE CODE\n")
        outfile.write("=========================================\n\n")
        
        # Write file structure first
        outfile.write("--- FILE STRUCTURE ---\n")
        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if d not in excluded_dirs]
            rel_path = os.path.relpath(root, root_dir)
            if rel_path == '.':
                indent = ""
            else:
                indent = "  " * rel_path.count(os.sep)
                outfile.write(f"{indent}📂 {os.path.basename(root)}/\n")
            
            for file in files:
                if file in excluded_files:
                    continue
                if file.endswith('.py') or file.endswith('.md') or file.endswith('.txt'):
                    file_indent = "  " * (rel_path.count(os.sep) + 1) if rel_path != '.' else "  "
                    outfile.write(f"{file_indent}📄 {file}\n")
        
        outfile.write("\n=========================================\n")
        outfile.write("--- FILE CONTENT ---\n")
        outfile.write("=========================================\n\n")
        
        # Write content of each file
        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if d not in excluded_dirs]
            for file in files:
                if file in excluded_files:
                    continue
                if file.endswith('.py') or file.endswith('.md') or file.endswith('.txt'):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, root_dir)
                    
                    outfile.write(f"=========================================\n")
                    outfile.write(f"FILE: {rel_path}\n")
                    outfile.write(f"=========================================\n")
                    try:
                        with open(full_path, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                            outfile.write(content)
                    except Exception as e:
                        outfile.write(f"Error reading file: {str(e)}\n")
                    outfile.write("\n\n")

if __name__ == "__main__":
    workspace = r"c:\Users\arulh\Desktop\Task_Breakdown"
    output_path = os.path.join(workspace, "project_codebase_dump.txt")
    print(f"Aggregating project files from {workspace} into {output_path}...")
    aggregate_files(workspace, output_path)
    print("Aggregation complete!")
