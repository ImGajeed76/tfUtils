import os
import shutil
from pathlib import Path
from typing import Optional

from src.lib.console import ask_input, ask_select, ask_yes_no
from src.lib.interface import interface
from src.lib.paths import NetworkPath
from src.lib.utils import console, safe_copy_directory

U_VISION_TEMPLATES_PATH = NetworkPath(r"T:\E\LIVE\06_SW_Entwicklung\11_Vorlagen")


def get_all_uv_templates():
    template_dirs = []

    for path in U_VISION_TEMPLATES_PATH.rglob("*"):
        if path.is_dir():
            if any(file.suffix in (".uvproj", ".uvprojx") for file in path.iterdir()):
                template_dirs.append(path)

    return template_dirs


def clean_directory(directory: Path) -> None:
    """Remove .bak files and Listing/Object directories."""
    # Remove .bak files
    for bak_file in directory.rglob("*.bak"):
        bak_file.unlink()

    # Remove Listing and Object directories
    for dir_name in ["Listing"]:
        dir_path = directory / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)

    # Remove files ending with .uvgui.*
    for file in directory.rglob("*.uvgui*"):
        file.unlink()


def rename_uv_files(directory: Path, new_name: str) -> None:
    """Rename only .uvopt, .uvproj, .uvoptx, and .uvprojx files in the directory."""
    for file_path in directory.glob("*"):
        if file_path.suffix.lower() in [".uvopt", ".uvproj", ".uvoptx", ".uvprojx"]:
            new_filename = f"{new_name}{file_path.suffix}"
            file_path.rename(file_path.parent / new_filename)


def remove_bat_scripts(directory: Path) -> None:
    """Remove all .bat files from the directory."""
    for bat_file in directory.rglob("*.bat"):
        bat_file.unlink()


def convert_to_clion(
    objects_folder_name: str, project_root: Optional[Path] = None
) -> None:
    """Convert uVision project to CLion project."""
    if project_root is None:
        project_root = Path.cwd()

    # Define the paths of the files to copy
    current_dir = Path(__file__).parent

    cmake_file = current_dir / "CMakeLists.txt"
    flash_bat = current_dir / "flash.bat"
    clang_format = current_dir / ".clang-format"
    workspace_config_file = current_dir / "workspace_config.xml"

    # Create .idea folder if it doesn't exist
    idea_folder = project_root / ".idea"
    idea_folder.mkdir(exist_ok=True)

    source_folder = project_root / "Source"
    # if the Source folder doesn't exist,
    # find it in the project root by looking for the main.c file
    if not source_folder.exists():
        main_c_files = list(project_root.rglob("main.c"))
        if main_c_files:
            source_folder = main_c_files[0].parent

    project_name = project_root.name

    # Copy files to the root of the project
    for file in [cmake_file, flash_bat, clang_format]:
        shutil.copy2(file, project_root)
        # rename $$SOURCE$$, $$NAME$$, $$OBJECTS$$
        with open(project_root / file.name, encoding="utf-8") as f:
            content = f.read()
            content = content.replace("$$SOURCE$$", str(source_folder.name))
            content = content.replace("$$NAME$$", project_name.replace(" ", "_"))
            content = content.replace("$$OBJECTS$$", objects_folder_name)
        with open(project_root / file.name, "w", encoding="utf-8") as f:
            f.write(content)

    # Handle workspace.xml
    workspace_xml_path = idea_folder / "workspace.xml"
    if workspace_xml_path.exists():
        with open(workspace_config_file) as config_file, open(
            workspace_xml_path, "a"
        ) as workspace_file:
            workspace_file.write(config_file.read())
    else:
        shutil.copy2(workspace_config_file, workspace_xml_path)


@interface("Neues uVision Projekt", activate=U_VISION_TEMPLATES_PATH.is_valid)
def create_new_project():
    console.print("uVision Templates werden geladen...")

    template_paths = get_all_uv_templates()

    # sort the templates by path
    template_paths.sort()

    template_names = [
        str(path.relative_to(U_VISION_TEMPLATES_PATH)) for path in template_paths
    ]

    template_index = ask_select("Wähle eine uVision Vorlage", template_names)
    template_path = template_paths[template_index]

    suggested_name = Path(os.getcwd()).name
    project_name = ask_input(
        "Projekt Name",
        description="Wie möchtest du dein uVision Projekt nennen?",
        placeholder=suggested_name,
    )

    use_new = ask_yes_no(
        "Neuen Ordner erstellen?",
        f"Möchtest du einen neuen Ordner mit dem namen "
        f"'{project_name}' in diesem Ordner erstellen?\n"
        f"Der neue Pfad währe dann: ./{Path.cwd().name}/{project_name}",
    )

    if use_new:
        new_dir_path = Path.cwd() / project_name
        new_dir_path.mkdir(exist_ok=True)
    else:
        new_dir_path = Path.cwd()

    # Copy the template folder contents to the new directory
    safe_copy_directory(template_path, new_dir_path)

    # Clean the directory (remove .bak files and Listing/Object directories)
    clean_directory(new_dir_path)

    # Ask for version (pattern: vX.Y)
    version = ask_input(
        "Version",
        description="Bitte gebe die Versionsnummer ein (VX.Y)",
        regex=r"V\d+\.\d+",
        placeholder="V1.0",
    )

    # Rename uVision files
    new_name = f"{project_name}_{version}"
    rename_uv_files(new_dir_path, new_name)

    # Remove .bat scripts
    remove_bat_scripts(new_dir_path)

    console.print(
        f"[green]Successfully[/green] copied template to "
        f"[yellow]{new_dir_path}[/yellow]"
    )

    # Ask if the user wants to modify the project for CLion
    modify_clion = ask_yes_no(
        "Projekt für CLion anpassen?", "Möchtest du das Projekt für CLion anpassen?"
    )
    if modify_clion:
        os.chdir(new_dir_path)
        convert_to_clion_wrapper()


def in_u_vision_project() -> bool:
    uvproj_files = list(Path().cwd().glob("*.uvproj*"))
    return bool(uvproj_files)


@interface("zu CLion Projekt konvertieren", in_u_vision_project())
def convert_to_clion_wrapper():
    current_dir = Path.cwd()
    objects_folder_name = "Object"
    for name in ["Objects", "Object", "objects", "object"]:
        if (current_dir / name).exists():
            objects_folder_name = name
            break

    convert_to_clion(objects_folder_name, current_dir)
    console.print("[green]Successfully[/green] modified project for CLion")
