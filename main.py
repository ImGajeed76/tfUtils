"""
Interface Selection Tool
This script provides a command-line interface for selecting and executing
interface functions from a specified directory structure.
"""

import importlib
import inspect
import os
import sys
from pathlib import Path
from typing import Callable, Dict, List, Optional, TypedDict

from rich.prompt import Prompt

from src.lib.console import ask_select
from src.lib.paths import check_paths
from src.lib.utils import console


# Type definitions
class InterfaceFunction(TypedDict):
    name: str
    function: Callable
    module: str


# Constants
MAIN_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
INTERFACES_BASE_PATH = MAIN_DIR / "src" / "interfaces"

# Add main directory to Python path
sys.path.insert(0, str(MAIN_DIR))


def scan_for_interface_functions(module_name: str) -> List[InterfaceFunction]:
    """
    Scan a module for interface functions with specific attributes.

    Args:
        module_name: The name of the module to scan

    Returns:
        List of dictionaries containing interface function information
    """
    try:
        module = importlib.import_module(module_name)
        all_functions = inspect.getmembers(module, inspect.isfunction)

        interface_functions = [
            {"name": func._NAME, "function": func, "module": module_name}
            for name, func in all_functions
            if hasattr(func, "_IS_INTERFACE")
            and func._IS_INTERFACE
            and hasattr(func, "_NAME")
        ]

        return interface_functions
    except Exception:
        return []


def scan_directory(base_path: Path) -> Dict[str, List[InterfaceFunction]]:
    """
    Recursively scan a directory for Python files containing interface functions.

    Args:
        base_path: The base directory path to scan

    Returns:
        Dictionary mapping directory paths to lists of interface functions
    """
    tree = {}

    for item in base_path.rglob("*.py"):
        relative_path = item.relative_to(INTERFACES_BASE_PATH)
        module_name = ".".join(
            ("src", "interfaces") + relative_path.with_suffix("").parts
        )

        interface_funcs = scan_for_interface_functions(module_name)
        if interface_funcs:
            folder_path = str(relative_path.parent).replace("\\", "/")
            folder_path = "" if folder_path == "." else folder_path

            if folder_path not in tree:
                tree[folder_path] = []
            tree[folder_path].extend(interface_funcs)

    return tree


def select_function(tree: Dict[str, List[InterfaceFunction]]) -> Optional[Callable]:
    """
    Interactive function selection interface.

    Args:
        tree: Dictionary containing the interface function tree

    Returns:
        Selected function or None if no selection was made
    """
    current_path = ""

    while True:
        choices = []
        functions = []
        subdirectories = set()

        # Get functions for current path
        if current_path in tree:
            functions = tree[current_path]
            choices.extend([func["name"] for func in functions])

        # Get subdirectories
        for path in tree.keys():
            parts = path.split("/")
            if current_path == "" and len(parts) > 0:
                subdirectories.add(parts[0])
            elif path.startswith(current_path + "/"):
                next_level = parts[len(current_path.split("/")) if current_path else 0]
                if next_level:
                    subdirectories.add(next_level)

        # Clean up and sort choices
        choices.extend(sorted(subdirectories))
        choices = [choice for choice in choices if choice]

        # Add parent directory option
        if current_path:
            choices.insert(0, "..")

        if not choices:
            console.print(f"No actions available in {current_path or 'Root'}")
            return None

        # Present selection prompt
        prompt = (
            f"Wähle eine Aktion{' (' + current_path + ')' if current_path else ''}:"
        )
        selection = ask_select(prompt, choices)

        # Handle selection
        if selection == 0 and current_path:  # Parent directory
            current_path = "/".join(current_path.split("/")[:-1])
        elif selection < len(functions) + (1 if current_path else 0):  # Function
            return functions[selection - (1 if current_path else 0)]["function"]
        elif selection < len(choices):  # Subdirectory
            selected_dir = choices[selection]
            current_path = f"{current_path}/{selected_dir}".lstrip("/")
        else:
            console.print("Invalid selection")
            return None


def main() -> None:
    """Main execution function."""
    console.clear()
    console.print(
        "[bright_black]Starting the interface selection tool...[/bright_black]"
    )

    # Check required paths
    if not check_paths():
        sys.exit(1)

    console.print("[bright_black]Startup finished![/bright_black]")
    console.print(f"Du befindest dich in: [yellow]{Path.cwd()}[/yellow]")

    # Confirm execution
    continue_execution = (
        Prompt.ask("Möchtest du fortfahren?", choices=["y", "n"]) == "y"
    )

    if not continue_execution:
        sys.exit(0)

    # Scan and execute
    tree = scan_directory(INTERFACES_BASE_PATH)
    selected_function = select_function(tree)

    if selected_function:
        try:
            console.clear()
            selected_function()
        except Exception as e:
            console.print(
                f"[red]An error occurred while executing the function: {e}[/red]"
            )
    else:
        console.print("No function selected")


if __name__ == "__main__":
    main()
