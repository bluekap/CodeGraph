from pathlib import Path
from typing import Optional

try:
    from langchain_core.tools import tool
except ImportError:
    # Define a dummy decorator if langchain is not installed
    def tool(func):
        return func

@tool
def get_repository_architecture(path: str) -> str:
    """
    Returns the high-level architecture overview and mermaid diagram of the repository.
    Useful for understanding the repository's structure at a glance.
    """
    file_path = Path(path) / ".agents" / "codegraph" / "architecture.md"
    if file_path.exists():
        return file_path.read_text()
    return "Architecture file not found. Please run 'codegraph analyze' first."

@tool
def get_module_details(path: str) -> str:
    """
    Returns a breakdown of the functions, classes, and their docstrings in the repository.
    Useful for finding specific functions or understanding what a module exports.
    """
    file_path = Path(path) / ".agents" / "codegraph" / "modules.md"
    if file_path.exists():
        return file_path.read_text()
    return "Modules file not found. Please run 'codegraph analyze' first."

@tool
def get_complexity_hotspots(path: str) -> str:
    """
    Returns the list of the most complex files and functions in the repository.
    Useful for finding technical debt or areas that might be difficult to debug.
    """
    file_path = Path(path) / ".agents" / "codegraph" / "hotspots.md"
    if file_path.exists():
        return file_path.read_text()
    return "Hotspots file not found. Please run 'codegraph analyze' first."
