import getpass
import os
from datetime import datetime
from pathlib import Path

from rich.prompt import Prompt

from src.lib.console import ask_select, ask_input, ask_yes_no
from src.lib.interface import interface
from src.lib.paths import PATHS
from src.lib.utils import safe_copy_directory, console


def get_all_schema_layout_templates():
    template_dirs = []

    for path in PATHS["ALTIUM_TEMPLATES_PATH"].rglob('*'):
        if path.is_dir():
            if any(file.suffix in ('.PRJPCB') for file in path.iterdir()):
                template_dirs.append(path)

    return template_dirs


@interface("Neues Altium Projekt")
def new_altium_project(default_name=None, create_new_dir=None):
    if default_name is None:
        default_name = Path.cwd().name

    template_paths = get_all_schema_layout_templates()

    # sort the templates by path
    template_paths.sort()

    template_names = [str(path.relative_to(PATHS["ALTIUM_TEMPLATES_PATH"])) for path in template_paths]

    template_index = ask_select("Select an Altium Template", choices=template_names)
    template_path = template_paths[template_index]

    project_name = ask_input("Projekt Name", "Was ist der Name deines Altium Projekts", placeholder=default_name)

    project_path = Path.cwd()

    if create_new_dir is None:
        use_new = ask_yes_no("Neuen Ordner erstellen?",
                             f"Möchtest du einen neuen Ordner mit dem namen '{project_name}' in diesem Ordner erstellen?\nDer neue Pfad währe dann: ./{Path.cwd().name}/{project_name}")
    else:
        use_new = create_new_dir

    if use_new:
        project_path = project_path / project_name
        project_path.mkdir(exist_ok=True, parents=True)

    safe_copy_directory(template_path, project_path)

    console.print(f"[green]Successfully[/green] copied template to [yellow]{project_path}[/yellow]")

    # Run post-copy operations
    update_project_version(project_path, "V1.0")
    rename_project(project_path, project_name)

    console.print(f"[green]Successfully[/green] updated project version and renamed project")


def update_project_version(project_path: Path, version=None):
    os.chdir(project_path)
    # Extract old project name and version
    old_filename = next(Path.cwd().glob('*.PRJPCB')).stem
    project_name, old_project_version = old_filename.split('_')
    old_project_version = old_project_version[1:]

    # Extract Version
    old_project_version_major = 1
    old_project_version_minor = 0
    if '.' in old_project_version:
        old_project_version_major, old_project_version_minor = old_project_version.split('.')
        old_project_version_major = int(old_project_version_major)
        old_project_version_minor = int(old_project_version_minor)
    elif old_project_version[1:].isnumeric():
        old_project_version_major = int(old_project_version)

    # Get new version
    if version is None:
        console.print("The new version number is composed as follows:")
        console.print("[yellow]x[/yellow].[magenta]y[/magenta]")
        console.print("| |")
        console.print("| +------- [magenta]Minor version[/magenta] number (extensions & bug fixes)")
        console.print(
            "+--------- [yellow]Major version[/yellow] number (new start / extremely significant change / no backward compatibility)")
        console.print()
        console.print(f"Old project version: {old_project_version_major}.{old_project_version_minor}")

        new_minor_release = None

        new_major_release = Prompt.ask("New major version number")
        while True:
            # ask the user for major version number until they enter a valid number
            # valid is any number greater or equal to the old major version number
            # or a version of x.y where x is greater or equal than the old major version number
            # or y is greater than the old minor version number
            if new_major_release.isnumeric():
                if int(new_major_release) >= int(old_project_version_major):
                    new_major_release = int(new_major_release)
                    break
            elif '.' in new_major_release:
                major, minor = new_major_release.split('.')
                if not (major.isnumeric() and minor.isnumeric()):
                    continue

                major = int(major)
                minor = int(minor)
                if major > old_project_version_major:
                    new_major_release = major
                    new_minor_release = minor
                    break
                elif major == old_project_version_major and minor > old_project_version_minor:
                    new_major_release = major
                    new_minor_release = minor
                    break
            new_major_release = Prompt.ask(
                "New major version number (must be greater or equal to the old major version number)")

        if new_minor_release is None:
            new_minor_release = Prompt.ask("New minor version number")

            while True:
                if new_minor_release.isnumeric():
                    if int(new_minor_release) > old_project_version_minor:
                        new_minor_release = int(new_minor_release)
                        break
                new_minor_release = Prompt.ask(
                    "New minor version number (must be greater than the old minor version number)")

        new_project_version = f"V{new_major_release}.{new_minor_release}"

        # Get comment
        comment = Prompt.ask("History comment")

    else:
        new_project_version = version
        comment = "Initial Project Creation"

    # Get user initials
    user = getpass.getuser().split('\\')[-1][-4:]
    user = Prompt.ask("User initials", default=user)

    # Get current date
    date = datetime.now().strftime("%m/%d/%Y")

    # New filename (without extension)
    new_filename = f"{project_name}_{new_project_version}"

    # Rename files
    _rename_files(project_path, old_filename, new_filename, project_name, old_project_version, new_project_version)

    # Edit project files
    _edit_project_files(project_path, old_filename, new_filename, project_name, old_project_version,
                        new_project_version)

    # Update history file
    history_line = f"{new_project_version[1:]}\t\t{user}\t{date}\t{comment}"
    with open('_history.txt', 'a') as f:
        f.write(history_line + '\n')

    console.print("[green]Project version updated successfully.[/green]")


def rename_project(project_path: Path, new_project_name=None):
    os.chdir(project_path)

    # Extract old project name and version
    old_filename = next(Path.cwd().glob('*.PRJPCB')).stem
    old_project_name, project_version = old_filename.split('_')

    # Display old project name
    console.print(f"Old project name: {old_project_name}")

    # Get new project name
    if not new_project_name:
        new_project_name = Prompt.ask("Enter the new project name")

    # New filename (without extension)
    new_filename = f"{new_project_name}_{project_version}"

    # Rename files
    _rename_files(project_path, old_filename, new_filename, old_project_name, project_version, project_version,
                  new_project_name)

    # Edit project files
    _edit_project_files(project_path, old_filename, new_filename, old_project_name, project_version, project_version,
                        new_project_name)

    console.print("[green]Project renamed successfully.[/green]")


def _rename_files(project_path: Path, old_filename, new_filename, project_name, old_version, new_version,
                  new_project_name=None):
    new_project_name = new_project_name or project_name
    file_mappings = [
        (f"{old_filename}.PRJPCB", f"{new_filename}.PRJPCB"),
        (f"{old_filename}.OutJob", f"{new_filename}.OutJob"),
        (f"Layout/{old_filename}.PcbDoc", f"Layout/{new_filename}.PcbDoc"),
        (f"Layout/{project_name}_Panel_{old_version}.PcbDoc",
         f"Layout/{new_project_name}_Panel_{new_version}.PcbDoc"),
        (f"Layout/{old_filename}.PcbLib", f"Layout/{new_filename}.PcbLib"),
        (f"Schema/{old_filename}.SchDoc", f"Schema/{new_filename}.SchDoc"),
        (f"Schema/{project_name}_Blockschema_{old_version}.SchDoc",
         f"Schema/{new_project_name}_Blockschema_{new_version}.SchDoc"),
        (f"Schema/{old_filename}.SchLib", f"Schema/{new_filename}.SchLib"),
    ]

    for old_path, new_path in file_mappings:
        old_full_path = project_path / old_path
        new_full_path = project_path / new_path
        if old_full_path.exists():
            old_full_path.rename(new_full_path)


def _edit_project_files(project_path: Path, old_filename, new_filename, project_name, old_version, new_version,
                        new_project_name=None):
    new_project_name = new_project_name or project_name
    file_paths = [f"{new_filename}.PRJPCB", f"{new_filename}.OutJob"]

    for file_path in file_paths:
        full_path = project_path / file_path
        if full_path.exists():
            with open(full_path, 'r') as file:
                content = file.read()

            replacements = [
                (f"{old_filename}.OutJob", f"{new_filename}.OutJob"),
                (f"{old_filename}.PcbDoc", f"{new_filename}.PcbDoc"),
                (f"{project_name}_Panel_{old_version}.PcbDoc", f"{new_project_name}_Panel_{new_version}.PcbDoc"),
                (f"{old_filename}.PcbLib", f"{new_filename}.PcbLib"),
                (f"{old_filename}.SchDoc", f"{new_filename}.SchDoc"),
                (f"{project_name}_Blockschema_{old_version}.SchDoc",
                 f"{new_project_name}_Blockschema_{new_version}.SchDoc"),
                (f"{old_filename}.SchLib", f"{new_filename}.SchLib"),
            ]

            for old, new in replacements:
                content = content.replace(old, new)

            with open(full_path, 'w') as file:
                file.write(content)


def is_altium_project() -> bool:
    return any(file.suffix in ('.PRJPCB') for file in Path.cwd().rglob('*.PRJPCB'))


@interface("Altium Projekt umbenennen", is_altium_project())
def rename_altium_project():
    for path in Path.cwd().rglob('*.PRJPCB'):
        project_path = path.parent
        break

    console.print(f"Project path: [yellow]{project_path}[/yellow]")

    rename_project(project_path)

    console.print(f"[green]Successfully[/green] renamed project")


@interface("Altium Projekt Version ändern", is_altium_project())
def run():
    for path in Path.cwd().rglob('*.PRJPCB'):
        project_path = path.parent
        break

    console.print(f"Project path: [yellow]{project_path}[/yellow]")

    update_project_version(project_path)

    console.print(f"[green]Successfully[/green] updated project version")
