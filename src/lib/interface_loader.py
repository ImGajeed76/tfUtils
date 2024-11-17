import inspect
from importlib import import_module
from pathlib import Path
from typing import Callable, Coroutine, List, NamedTuple

from textual.containers import Container

from src.lib.interface_viewer import InterfaceReference


class InterfaceInfo(NamedTuple):
    """Container for interface information"""

    name: str
    path: str
    description: str
    is_active: Callable[[], bool]
    callback: Callable[[Container], Coroutine]
    import_path: str
    module_path: str

    def __str__(self):
        return f"Interface: {self.name} ({'Active' if self.is_active else 'Inactive'})"

    def __repr__(self):
        return f"""InterfaceInfo:
- name: {self.name}
- description: {self.description}
- is_active: {self.is_active}
- callback: {self.callback}
        """

    def generate_import(self) -> str:
        """
        Generates import statements for the interface.

        Returns:
            String containing import statements
        """
        imports = [f"from {self.module_path} import {self.callback.__name__}"]

        if callable(self.is_active) and hasattr(self.is_active, "__name__"):
            is_active_name = self.is_active.__name__
            if not is_active_name.startswith("<"):
                imports.append(f"from {self.module_path} import {is_active_name}")

        return "\n".join(imports)


def scan_interfaces(folder_path: Path, src_path: Path) -> List[InterfaceInfo]:
    """
    Scans a folder for Python files and extracts interface information.

    Args:
        folder_path: Path to the folder containing interface files
        src_path: Path to the src folder

    Returns:
        List of InterfaceInfo objects containing interface details
    """
    interfaces = []

    for file in folder_path.glob("**/*.py"):
        module_path = str(
            file.relative_to(src_path.parent).with_suffix("").as_posix()
        ).replace("/", ".")

        try:
            module = import_module(module_path)

            functions = [
                getattr(module, func_name)
                for func_name in dir(module)
                if callable(getattr(module, func_name, None))
            ]

            for func in functions:
                if hasattr(func, "_IS_INTERFACE"):
                    interface_info = InterfaceInfo(
                        name=getattr(func, "_NAME", "Unnamed Interface"),
                        path=file.relative_to(folder_path).with_suffix("").as_posix(),
                        description=inspect.getdoc(func) or "",
                        is_active=getattr(func, "_ACTIVATE", True),
                        callback=func,
                        import_path=f"{module_path}.{func.__name__}",
                        module_path=module_path,
                    )
                    interfaces.append(interface_info)

        except ImportError as e:
            print(f"Failed to import {file}: {e}")
            continue

    return interfaces


def create_interface_references(
    interface_infos: List[InterfaceInfo],
) -> List[InterfaceReference]:
    """
    Converts InterfaceInfo objects to InterfaceReference objects.

    Args:
        interface_infos: List of InterfaceInfo objects

    Returns:
        List of InterfaceReference objects
    """
    return [
        InterfaceReference(
            path=f"root/{interface_info.path}",
            name=interface_info.name,
            description=interface_info.description,
            call_back=interface_info.callback,
            active=interface_info.is_active(),
        )
        for interface_info in interface_infos
    ]


def create_folder_references(
    interface_infos: List[InterfaceInfo],
    interface_folder_path: Path,
) -> List[InterfaceReference]:
    """
    Converts folders to InterfaceReference objects.

    Args:
        interface_infos: List of InterfaceInfo objects
        interface_folder_path: Path to the folder containing interface files

    Returns:
        List of InterfaceReference objects
    """
    references = []

    interface_paths = [interface_info.path for interface_info in interface_infos]
    folder_paths = set()
    for interface_path in interface_paths:
        interface_folder = interface_path.split("/")
        for i in range(1, len(interface_folder)):
            folder_paths.add("/".join(interface_folder[:i]))

    for folder_path in folder_paths:
        info_file = interface_folder_path / folder_path / "info.md"
        info_text = "Folder (no info.md)"
        if info_file.exists():
            with info_file.open("r") as f:
                info_text = f.read().strip()

        references.append(
            InterfaceReference(
                path=f"root/{folder_path}",
                name=folder_path.split("/")[-1],
                description=info_text,
                active=True,
            )
        )

    return references
