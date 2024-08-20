import importlib
import inspect
import os
import sys
from pathlib import Path
from typing import Dict, List, Callable, Union

from rich.prompt import Prompt

from src.lib.console import ask_select
from src.lib.paths import check_paths
from src.lib.utils import console

MAIN_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
INTERFACES_BASE_PATH = MAIN_DIR / "src" / "interfaces"
sys.path.insert(0, str(MAIN_DIR))

def scan_for_interface_functions(module_name: str) -> List[Dict[str, any]]:
    try:
        module = importlib.import_module(module_name)
        all_functions = inspect.getmembers(module, inspect.isfunction)
        interface_functions = [
            {"name": func._NAME, "function": func, "module": module_name}
            for name, func in all_functions
            if hasattr(func, '_IS_INTERFACE') and func._IS_INTERFACE and hasattr(func, '_NAME')
        ]
        return interface_functions
    except Exception:
        return []

def scan_directory(base_path: Path) -> Dict[str, List[Dict[str, any]]]:
    tree = {}
    for item in base_path.rglob('*.py'):
        relative_path = item.relative_to(INTERFACES_BASE_PATH)
        module_name = '.'.join(('src', 'interfaces') + relative_path.with_suffix('').parts)
        interface_funcs = scan_for_interface_functions(module_name)
        if interface_funcs:
            folder_path = str(relative_path.parent).replace('\\', '/')
            if folder_path == '.':
                folder_path = ''
            if folder_path not in tree:
                tree[folder_path] = []
            tree[folder_path].extend(interface_funcs)
    return tree

def select_function(tree: Dict[str, List[Dict[str, any]]]) -> Union[Callable, None]:
    current_path = ''
    while True:
        choices = []
        functions = []
        subdirectories = set()

        if current_path in tree:
            functions = tree[current_path]
            choices.extend([func['name'] for func in functions])

        for path in tree.keys():
            parts = path.split('/')
            if current_path == '' and len(parts) > 0:
                subdirectories.add(parts[0])
            elif path.startswith(current_path + '/'):
                next_level = parts[len(current_path.split('/')) if current_path else 0]
                if next_level:
                    subdirectories.add(next_level)

        choices.extend(sorted(subdirectories))

        # Remove empty option
        choices = [choice for choice in choices if choice]

        if current_path:  # Add '..' option if not at root
            choices.insert(0, '..')

        if not choices:
            print(f"No actions available in {current_path or 'Root'}")
            return None

        prompt = f"Wähle eine Aktion{' (' + current_path + ')' if current_path else ''}:"
        selection = ask_select(prompt, choices)

        if selection == 0 and current_path:  # '..' selected
            current_path = '/'.join(current_path.split('/')[:-1])
        elif selection < len(functions) + (1 if current_path else 0):  # Function selected
            return functions[selection - (1 if current_path else 0)]['function']
        elif selection < len(choices):  # Subdirectory selected
            selected_dir = choices[selection]
            current_path = f"{current_path}/{selected_dir}".lstrip('/')
        else:
            print("Invalid selection")
            return None

if __name__ == "__main__":
    console.clear()
    console.print("[bright_black]Starting the interface selection tool... [/bright_black]")

    # check paths
    if not check_paths():
        sys.exit(1)

    # print startup finished
    console.print("[bright_black]Startup finished![/bright_black]")

    console.print(f"Du befindest dich in: [yellow]{Path.cwd()}[/yellow]")
    continue_execution = Prompt.ask("Möchtest du fortfahren?", choices=["y", "n"]) == "y"

    if not continue_execution:
        sys.exit(0)

    tree = scan_directory(INTERFACES_BASE_PATH)
    selected_function = select_function(tree)
    if selected_function:
        try:
            console.clear()
            selected_function()
        except Exception as e:
            print(f"An error occurred while executing the function: {e}")
    else:
        print("No function selected")