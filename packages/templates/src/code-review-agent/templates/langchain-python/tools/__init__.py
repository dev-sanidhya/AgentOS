"""
File operations, git tools, and specialized analysis tools for code review agent.
"""

from langchain.tools import Tool
import os
import fnmatch
from pathlib import Path
from typing import List, Optional
import git
import pygments
from pygments import highlight
from pygments.lexers import get_lexer_for_filename, get_lexer_by_name
from pygments.formatters import TerminalFormatter

# Import our specialized analysis tools
from .file_analyzer import CodeAnalyzerTool
from .security_scanner import SecurityScannerTool


def read_file(file_path: str) -> str:
    """
    Read and return the contents of a file.

    Args:
        file_path: Path to the file to read

    Returns:
        File contents as string
    """
    try:
        # Resolve relative paths
        file_path = os.path.expanduser(file_path)

        if not os.path.exists(file_path):
            return f"Error: File '{file_path}' does not exist"

        if not os.path.isfile(file_path):
            return f"Error: '{file_path}' is not a file"

        # Check if file is too large (limit to 50KB for analysis)
        file_size = os.path.getsize(file_path)
        if file_size > 50 * 1024:
            return f"Error: File '{file_path}' is too large ({file_size} bytes). Maximum size is 50KB"

        # Check if file is binary
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            if b'\0' in chunk:
                return f"Error: File '{file_path}' appears to be binary and cannot be reviewed"

        # Read the file
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Add syntax highlighting information
        try:
            lexer = get_lexer_for_filename(file_path)
            language = lexer.name
        except:
            language = "Unknown"

        return f"""File: {file_path}
Language: {language}
Size: {len(content)} characters
Lines: {len(content.splitlines())}

Content:
{content}"""

    except PermissionError:
        return f"Error: Permission denied reading '{file_path}'"
    except UnicodeDecodeError:
        return f"Error: Could not decode '{file_path}' as text"
    except Exception as e:
        return f"Error reading '{file_path}': {str(e)}"


def list_files(
    directory: str = ".",
    pattern: str = "*",
    recursive: bool = True,
    max_files: int = 100
) -> str:
    """
    List files in a directory with optional pattern matching.

    Args:
        directory: Directory to search (default: current directory)
        pattern: File pattern to match (default: all files)
        recursive: Search subdirectories (default: True)
        max_files: Maximum number of files to return (default: 100)

    Returns:
        Formatted list of matching files
    """
    try:
        directory = os.path.expanduser(directory)

        if not os.path.exists(directory):
            return f"Error: Directory '{directory}' does not exist"

        if not os.path.isdir(directory):
            return f"Error: '{directory}' is not a directory"

        files = []
        search_pattern = f"**/{pattern}" if recursive else pattern

        for file_path in Path(directory).glob(search_pattern):
            if file_path.is_file():
                # Skip hidden files and common ignore patterns
                if not any(part.startswith('.') for part in file_path.parts):
                    # Skip common binary and cache files
                    skip_patterns = [
                        '*.pyc', '*.pyo', '*.pyd', '__pycache__',
                        '*.so', '*.dll', '*.dylib',
                        '*.jpg', '*.jpeg', '*.png', '*.gif', '*.ico',
                        '*.zip', '*.tar', '*.gz', '*.bz2',
                        'node_modules', '.git', '.vscode', '.idea',
                        '*.min.js', '*.bundle.js'
                    ]

                    if not any(fnmatch.fnmatch(str(file_path), skip) for skip in skip_patterns):
                        relative_path = os.path.relpath(file_path, directory)
                        file_size = file_path.stat().st_size

                        # Only include reasonable-sized text files
                        if file_size < 100 * 1024:  # 100KB limit
                            files.append({
                                'path': relative_path,
                                'size': file_size,
                                'modified': file_path.stat().st_mtime
                            })

                if len(files) >= max_files:
                    break

        if not files:
            return f"No files found matching pattern '{pattern}' in '{directory}'"

        # Sort by modification time (newest first)
        files.sort(key=lambda x: x['modified'], reverse=True)

        result = f"Files in '{directory}' matching '{pattern}':\n"
        result += f"Found {len(files)} files (max {max_files} shown)\n\n"

        for file_info in files[:max_files]:
            size_str = f"{file_info['size']:,} bytes"
            result += f"{file_info['path']} ({size_str})\n"

        if len(files) > max_files:
            result += f"\n... and {len(files) - max_files} more files"

        return result

    except Exception as e:
        return f"Error listing files in '{directory}': {str(e)}"


def git_diff(base_branch: str = "main", target_branch: str = "HEAD") -> str:
    """
    Get git diff between branches.

    Args:
        base_branch: Base branch to compare against (default: "main")
        target_branch: Target branch to compare (default: "HEAD")

    Returns:
        Git diff output
    """
    try:
        # Try to initialize git repo
        repo = git.Repo(search_parent_directories=True)

        # Get the diff
        diff = repo.git.diff(f"{base_branch}...{target_branch}")

        if not diff:
            return f"No differences found between {base_branch} and {target_branch}"

        # Get list of changed files
        changed_files = repo.git.diff('--name-only', f"{base_branch}...{target_branch}").split('\n')
        changed_files = [f for f in changed_files if f.strip()]

        result = f"Git diff: {base_branch}...{target_branch}\n"
        result += f"Changed files: {len(changed_files)}\n\n"

        for file in changed_files:
            result += f"• {file}\n"

        result += f"\n{'='*50}\nDIFF CONTENT:\n{'='*50}\n\n"

        # Limit diff size to prevent overwhelming the LLM
        if len(diff) > 10000:  # 10KB limit
            result += diff[:10000]
            result += f"\n\n... (diff truncated - showing first 10KB of {len(diff)} total characters)"
        else:
            result += diff

        return result

    except git.InvalidGitRepositoryError:
        return "Error: Not in a git repository"
    except git.GitCommandError as e:
        return f"Git error: {str(e)}"
    except Exception as e:
        return f"Error getting git diff: {str(e)}"


# Create LangChain tools for file operations
file_read_tool = Tool(
    name="file_read",
    description="Read the contents of a file. Input should be a file path string.",
    func=read_file
)

file_list_tool = Tool(
    name="file_list",
    description="List files in a directory. Input format: 'directory,pattern,recursive' (e.g., 'src,*.py,true'). All parameters are optional.",
    func=lambda input_str: list_files(*input_str.split(',')) if ',' in input_str else list_files(input_str.strip())
)

git_diff_tool = Tool(
    name="git_diff",
    description="Get git diff between branches. Input format: 'base_branch,target_branch' (e.g., 'main,HEAD'). Default is 'main,HEAD'.",
    func=lambda input_str: git_diff(*input_str.split(',')) if ',' in input_str else git_diff(input_str.strip() if input_str.strip() else "main")
)

# Export all tools for easy import
__all__ = [
    'CodeAnalyzerTool',
    'SecurityScannerTool',
    'file_read_tool',
    'file_list_tool',
    'git_diff_tool'
]