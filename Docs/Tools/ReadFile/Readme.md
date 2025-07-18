# ReadLocalFile Module - ResearchGenie

The `ReadLocalFile` module provides a secure interface for reading local files from within a designated workspace folder. It supports multiple text-based file formats and ensures files can only be accessed within the workspace directory for security.

## Features
- **Secure File Access**: Only allows reading files within the workspace directory
- **Multiple File Formats**: Supports txt, json, markdown, csv
- **JSON Validation**: Automatically validates and formats JSON files
- **Encoding Support**: Configurable file encoding with UTF-8 default
- **Detailed Error Handling**: Comprehensive error reporting for file access issues
- **Two Interface Options**: Simple stringify method or detailed read_file method

## Basic Usage

```python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'Tools'))
from ReadLocalFile import ReadLocalFile

# Initialize with workspace path
reader = ReadLocalFile("/path/to/workspace")

# 1. Simple string output
content = reader.stringify("data.txt")
print(content)

# 2. Read with detailed response
result = reader.read_file("config.json")
if result['success']:
    print(f"File: {result['file_info']['name']}")
    print(f"Size: {result['file_info']['size']} bytes")
    print(result['content'])
else:
    print(f"Error: {result['error']}")

# 3. Read markdown file
markdown_content = reader.stringify("README.md")
print(markdown_content)

# 4. Check supported extensions
extensions = reader.get_supported_extensions()
print(f"Supported formats: {extensions}")
```

## Example: Reading Different File Types

```python
reader = ReadLocalFile()

# Read text file
text_content = reader.stringify("notes.txt")
print("Text content:", text_content[:100])

# Read JSON with validation
json_result = reader.read_file("settings.json")
if json_result['success']:
    print("Valid JSON:", json_result['content'][:200])
    print(f"File size: {json_result['file_info']['size']} bytes")

# Read Python source code
code_content = reader.stringify("data.csv")
print("CSV data:", code_content[:150])
```

## Example: Error Handling

```python
reader = ReadLocalFile("/secure/workspace")

# Attempt to read file outside workspace (will fail)
result = reader.read_file("/etc/passwd")
if not result['success']:
    print(f"Security check: {result['error']}")

# Attempt to read unsupported file type
result = reader.read_file("image.png")
if not result['success']:
    print(f"Unsupported format: {result['error']}")

# Handle encoding issues
result = reader.read_file("data.txt", encoding="latin1")
if result['success']:
    print("Content with custom encoding:", result['content'][:100])
```

## Example: Workspace Management

```python
reader = ReadLocalFile()

# Get current workspace
current_workspace = reader.get_workspace_path()
print(f"Current workspace: {current_workspace}")

# Change workspace
success = reader.set_workspace_path("/new/workspace/path")
if success:
    print("Workspace changed successfully")
else:
    print("Failed to change workspace")

# Read file from new workspace
content = reader.stringify("project_file.md")
```

## Security Features

- **Path Validation**: Prevents directory traversal attacks
- **Workspace Restriction**: Files can only be read from within the designated workspace
- **Relative Path Support**: Automatically resolves relative paths to workspace
- **File Type Filtering**: Only allows reading of supported text-based file formats

## Supported File Extensions

- **Text**: `.txt`
- **Data**: `.json`, `.csv`
- **Documentation**: `.md`, `.markdown`

---

**Tip:** Always use relative paths when possible, and ensure your workspace is properly configured for maximum security.