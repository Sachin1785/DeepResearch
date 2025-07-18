import json
import os
from typing import Optional, Dict, Any

class ReadLocalFile:
    """
    A tool for reading local files from the workspace folder only.
    Supports txt, json, markdown, and csv file formats.
    """
    
    SUPPORTED_EXTENSIONS = {'.txt', '.json', '.md', '.markdown', '.csv'}
    
    def __init__(self, workspace_path: str = None):
        self.name = "ReadLocalFile"
        self.description = "Read local files from workspace folder and return their content as strings"
        
        # Set workspace path - if not provided, use current directory
        if workspace_path is None:
            self.workspace_path = os.getcwd()
        else:
            self.workspace_path = os.path.abspath(workspace_path)
    
    def _is_within_workspace(self, file_path: str) -> bool:
        """
        Check if the file path is within the workspace directory.
        
        Args:
            file_path (str): Path to check
            
        Returns:
            bool: True if path is within workspace, False otherwise
        """
        try:
            # Convert to absolute path
            abs_file_path = os.path.abspath(file_path)
            abs_workspace_path = os.path.abspath(self.workspace_path)
            
            # Check if file path starts with workspace path
            return abs_file_path.startswith(abs_workspace_path)
        except Exception:
            return False
    
    def read_file(self, file_path: str, encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        Read a file from the workspace and return its content as a string.
        
        Args:
            file_path (str): Path to the file to read (relative to workspace or absolute within workspace)
            encoding (str): File encoding (default: utf-8)
            
        Returns:
            Dict containing success status, content, file info, and any error messages
        """
        try:
            # If relative path, make it relative to workspace
            if not os.path.isabs(file_path):
                file_path = os.path.join(self.workspace_path, file_path)
            
            # Security check - ensure file is within workspace
            if not self._is_within_workspace(file_path):
                return {
                    'success': False,
                    'error': f"Access denied: File must be within workspace directory ({self.workspace_path})",
                    'content': None,
                    'file_info': None
                }
            
            # Validate file exists
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': f"File not found: {file_path}",
                    'content': None,
                    'file_info': None
                }
            
            # Check if it's a file (not directory)
            if not os.path.isfile(file_path):
                return {
                    'success': False,
                    'error': f"Path is not a file: {file_path}",
                    'content': None,
                    'file_info': None
                }
            
            # Get file extension
            file_extension = os.path.splitext(file_path)[1].lower()
            
            # Check if file type is supported
            if file_extension not in self.SUPPORTED_EXTENSIONS:
                return {
                    'success': False,
                    'error': f"Unsupported file type: {file_extension}. Supported types: {', '.join(self.SUPPORTED_EXTENSIONS)}",
                    'content': None,
                    'file_info': None
                }
            
            # Read file content
            with open(file_path, 'r', encoding=encoding) as file:
                content = file.read()
            
            # Get file info
            file_stats = os.stat(file_path)
            relative_path = os.path.relpath(file_path, self.workspace_path)
            file_info = {
                'name': os.path.basename(file_path),
                'path': file_path,
                'relative_path': relative_path,
                'size': file_stats.st_size,
                'extension': file_extension,
                'encoding': encoding
            }
            
            # Special handling for JSON files - validate and stringify
            if file_extension == '.json':
                try:
                    # Parse JSON to validate it
                    json_data = json.loads(content)
                    # Re-stringify with proper formatting
                    content = json.dumps(json_data, indent=2, ensure_ascii=False)
                except json.JSONDecodeError as e:
                    return {
                        'success': False,
                        'error': f"Invalid JSON format: {str(e)}",
                        'content': content,  # Return raw content even if JSON is invalid
                        'file_info': file_info
                    }
            
            return {
                'success': True,
                'content': content,
                'file_info': file_info,
                'error': None
            }
            
        except UnicodeDecodeError as e:
            return {
                'success': False,
                'error': f"Encoding error: {str(e)}. Try a different encoding.",
                'content': None,
                'file_info': None
            }
        except PermissionError:
            return {
                'success': False,
                'error': f"Permission denied: Cannot read file {file_path}",
                'content': None,
                'file_info': None
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}",
                'content': None,
                'file_info': None
            }
    
    def stringify(self, file_path: str, encoding: str = 'utf-8') -> str:
        """
        Read a file from the workspace and return its content as a string (simplified interface).
        
        Args:
            file_path (str): Path to the file to read (relative to workspace or absolute within workspace)
            encoding (str): File encoding (default: utf-8)
            
        Returns:
            str: File content as string, or error message if failed
        """
        result = self.read_file(file_path, encoding)
        
        if result['success']:
            return result['content']
        else:
            return f"Error reading file: {result['error']}"
    
