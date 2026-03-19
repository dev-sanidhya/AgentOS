"""
Tools package for {{AgentName}} CrewAI Code Review Agent

This package contains specialized tools for comprehensive code analysis:
- FileAnalyzer: Code structure, complexity, and syntax analysis
- SecurityScanner: Security vulnerability and threat detection

Author: {{author_name}}
Created: {{creation_date}}
"""

from .file_analyzer import FileAnalyzer, ComplexityVisitor
from .security_scanner import SecurityScanner, SecurityFinding

__version__ = "1.0.0"

__all__ = [
    "FileAnalyzer",
    "ComplexityVisitor",
    "SecurityScanner",
    "SecurityFinding"
]

# Tool registry for easy access
AVAILABLE_TOOLS = {
    "file_analyzer": FileAnalyzer,
    "security_scanner": SecurityScanner
}

def get_tool(tool_name: str):
    """
    Get a tool instance by name.

    Args:
        tool_name: Name of the tool to retrieve

    Returns:
        Tool instance or None if not found
    """
    tool_class = AVAILABLE_TOOLS.get(tool_name)
    if tool_class:
        return tool_class()
    return None

def list_available_tools():
    """
    List all available tools.

    Returns:
        List of available tool names
    """
    return list(AVAILABLE_TOOLS.keys())

def get_tool_descriptions():
    """
    Get descriptions of all available tools.

    Returns:
        Dictionary mapping tool names to descriptions
    """
    descriptions = {}
    for name, tool_class in AVAILABLE_TOOLS.items():
        tool_instance = tool_class()
        descriptions[name] = {
            "name": tool_instance.name,
            "description": tool_instance.description
        }
    return descriptions

# Initialize all tools for testing
def test_tools():
    """Test all tools for basic functionality."""
    results = {}

    for tool_name in AVAILABLE_TOOLS:
        try:
            tool = get_tool(tool_name)
            results[tool_name] = {
                "status": "available",
                "name": tool.name,
                "description": tool.description[:100] + "..." if len(tool.description) > 100 else tool.description
            }
        except Exception as e:
            results[tool_name] = {
                "status": "error",
                "error": str(e)
            }

    return results

if __name__ == "__main__":
    # Test tools when run directly
    print("Testing {{AgentName}} Tools...")
    print("=" * 50)

    test_results = test_tools()
    for tool_name, result in test_results.items():
        if result["status"] == "available":
            print(f"✓ {tool_name}: {result['name']}")
            print(f"  Description: {result['description']}")
        else:
            print(f"✗ {tool_name}: {result['error']}")
        print()

    print("Available tools:", list_available_tools())