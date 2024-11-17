import getpass
import os
from datetime import datetime
from pathlib import Path

from textual.containers import Container

from src.lib.console import ask_input, ask_select, ask_yes_no
from src.lib.interface import interface
from src.lib.paths import NetworkPath
from src.lib.utils import console, safe_copy_directory

ALTIUM_TEMPLATES_PATH = NetworkPath(
    r"T:\E\LIVE\05_HW_Entwicklung\02_Vorlage_Schema_Layout"
)


def get_all_schema_layout_templates():
    template_dirs = []

    for path in ALTIUM_TEMPLATES_PATH.rglob("*"):
        if path.is_dir():
            if any(file.suffix in (".PRJPCB") for file in path.iterdir()):
                template_dirs.append(path)

    return template_dirs


@interface("Neues Altium Projekt", activate=ALTIUM_TEMPLATES_PATH.exists)
async def new_altium_project(
    container: Container, default_name=None, create_new_dir=None
):
    if default_name is None:
        default_name = Path.cwd().name

    template_paths = get_all_schema_layout_templates()

    # sort the templates by path
    template_paths.sort()

    template_names = [
        str(path.relative_to(ALTIUM_TEMPLATES_PATH)) for path in template_paths
    ]

    template_path = await ask_select(
        container, "Select an Altium Template", options=template_names
    )

    project_name = await ask_input(
        container,
        "Was ist der Name deines Altium Projekts",
        placeholder=default_name,
    )

    project_path = Path.cwd()

    if create_new_dir is None:
        use_new = await ask_yes_no(
            container,
            (
                f"Möchtest du einen neuen Ordner mit dem namen '{project_name}' "
                f"in diesem Ordner erstellen?\n"
                f"Der neue Pfad währe dann: ./{Path.cwd().name}/{project_name}"
            ),
        )
    else:
        use_new = create_new_dir

    if use_new:
        project_path = project_path / project_name
        project_path.mkdir(exist_ok=True, parents=True)

    await safe_copy_directory(container, template_path, project_path)

    await console.print(
        container,
        f"[green]Successfully[/green] "
        f"copied template to [yellow]{project_path}[/yellow]",
    )

    # Run post-copy operations
    await update_project_version(container, project_path, "V1.0")
    await rename_project(container, project_path, project_name)

    await console.print(
        container,
        "[green]Successfully[/green] updated project version and renamed project",
    )


async def update_project_version(
    container: Container, project_path: Path, version=None
):
    os.chdir(project_path)
    # Extract old project name and version
    old_filename = next(Path.cwd().glob("*.PRJPCB")).stem
    project_name, old_project_version = old_filename.split("_")
    old_project_version = old_project_version[1:]

    # Extract Version
    old_project_version_major = 1
    old_project_version_minor = 0
    if "." in old_project_version:
        (
            old_project_version_major,
            old_project_version_minor,
        ) = old_project_version.split(".")
        old_project_version_major = int(old_project_version_major)
        old_project_version_minor = int(old_project_version_minor)
    elif old_project_version[1:].isnumeric():
        old_project_version_major = int(old_project_version)

    # Get new version
    if version is None:
        question = (
            "The new version number is composed as follows:\n"
            "[yellow]x[/yellow].[magenta]y[/magenta]\n"
            "| |\n"
            "| +------- [magenta]Minor version[/magenta] number "
            "(extensions & bug fixes)\n"
            "+--------- [yellow]Major version[/yellow] number "
            "(new start / extremely significant change / no backward compatibility)\n"
            "\n"
            f"Old project version: "
            f"{old_project_version_major}.{old_project_version_minor}\n"
        )

        regex = (
            rf"^(?:(?:${old_project_version_major + 1}\\d*\\.\\d+)|"
            rf"${old_project_version_major}\\.(?:[${old_project_version_minor + 1}-9]"
            rf"|\\d{2,}))$"
        )

        user_input = await ask_input(
            container,
            question,
            regex=regex,
            placeholder=f"{old_project_version_major}.{old_project_version_minor + 1}",
        )

        new_major_release, new_minor_release = user_input.split(".")
        new_project_version = f"V{new_major_release}.{new_minor_release}"

        # Get comment
        comment = await ask_input(
            container,
            "What is the reason for this version update?",
            placeholder="Initial Project Creation",
        )

    else:
        new_project_version = version
        comment = "Initial Project Creation"

    # Get user initials
    user = getpass.getuser().split("\\")[-1][-4:]
    user = await ask_input(container, "User initials", placeholder=user)

    # Get current date
    date = datetime.now().strftime("%m/%d/%Y")

    # New filename (without extension)
    new_filename = f"{project_name}_{new_project_version}"

    # Rename files
    _rename_files(
        project_path,
        old_filename,
        new_filename,
        project_name,
        old_project_version,
        new_project_version,
    )

    # Edit project files
    _edit_project_files(
        project_path,
        old_filename,
        new_filename,
        project_name,
        old_project_version,
        new_project_version,
    )

    # Update history file
    history_line = f"{new_project_version[1:]}\t\t{user}\t{date}\t{comment}"
    with open("_history.txt", "a") as f:
        f.write(history_line + "\n")

    await console.print(
        container, "[green]Project version updated successfully.[/green]"
    )


async def rename_project(
    container: Container, project_path: Path, new_project_name=None
):
    os.chdir(project_path)

    # Extract old project name and version
    old_filename = next(Path.cwd().glob("*.PRJPCB")).stem
    old_project_name, project_version = old_filename.split("_")

    # Display old project name
    await console.print(container, f"Old project name: {old_project_name}")

    # Get new project name
    if not new_project_name:
        new_project_name = await ask_input(container, "Enter the new project name")

    # New filename (without extension)
    new_filename = f"{new_project_name}_{project_version}"

    # Rename files
    _rename_files(
        project_path,
        old_filename,
        new_filename,
        old_project_name,
        project_version,
        project_version,
        new_project_name,
    )

    # Edit project files
    _edit_project_files(
        project_path,
        old_filename,
        new_filename,
        old_project_name,
        project_version,
        project_version,
        new_project_name,
    )

    await console.print(container, "[green]Project renamed successfully.[/green]")


def _rename_files(
    project_path: Path,
    old_filename,
    new_filename,
    project_name,
    old_version,
    new_version,
    new_project_name=None,
):
    new_project_name = new_project_name or project_name
    file_mappings = [
        (f"{old_filename}.PRJPCB", f"{new_filename}.PRJPCB"),
        (f"{old_filename}.OutJob", f"{new_filename}.OutJob"),
        (f"Layout/{old_filename}.PcbDoc", f"Layout/{new_filename}.PcbDoc"),
        (
            f"Layout/{project_name}_Panel_{old_version}.PcbDoc",
            f"Layout/{new_project_name}_Panel_{new_version}.PcbDoc",
        ),
        (f"Layout/{old_filename}.PcbLib", f"Layout/{new_filename}.PcbLib"),
        (f"Schema/{old_filename}.SchDoc", f"Schema/{new_filename}.SchDoc"),
        (
            f"Schema/{project_name}_Blockschema_{old_version}.SchDoc",
            f"Schema/{new_project_name}_Blockschema_{new_version}.SchDoc",
        ),
        (f"Schema/{old_filename}.SchLib", f"Schema/{new_filename}.SchLib"),
    ]

    for old_path, new_path in file_mappings:
        old_full_path = project_path / old_path
        new_full_path = project_path / new_path
        if old_full_path.exists():
            old_full_path.rename(new_full_path)


def _edit_project_files(
    project_path: Path,
    old_filename,
    new_filename,
    project_name,
    old_version,
    new_version,
    new_project_name=None,
):
    new_project_name = new_project_name or project_name
    file_paths = [f"{new_filename}.PRJPCB", f"{new_filename}.OutJob"]

    for file_path in file_paths:
        full_path = project_path / file_path
        if full_path.exists():
            with open(full_path) as file:
                content = file.read()

            replacements = [
                (f"{old_filename}.OutJob", f"{new_filename}.OutJob"),
                (f"{old_filename}.PcbDoc", f"{new_filename}.PcbDoc"),
                (
                    f"{project_name}_Panel_{old_version}.PcbDoc",
                    f"{new_project_name}_Panel_{new_version}.PcbDoc",
                ),
                (f"{old_filename}.PcbLib", f"{new_filename}.PcbLib"),
                (f"{old_filename}.SchDoc", f"{new_filename}.SchDoc"),
                (
                    f"{project_name}_Blockschema_{old_version}.SchDoc",
                    f"{new_project_name}_Blockschema_{new_version}.SchDoc",
                ),
                (f"{old_filename}.SchLib", f"{new_filename}.SchLib"),
            ]

            for old, new in replacements:
                content = content.replace(old, new)

            with open(full_path, "w") as file:
                file.write(content)


def is_altium_project() -> bool:
    return any(file.suffix in (".PRJPCB") for file in Path.cwd().rglob("*.PRJPCB"))


@interface("Altium Projekt umbenennen", is_altium_project)
async def rename_altium_project(container: Container):
    project_path = None
    for path in Path.cwd().rglob("*.PRJPCB"):
        project_path = path.parent
        break

    if not project_path:
        await console.print(container, "[red]No Altium project found[/red]")
        return

    await console.print(container, f"Project path: [yellow]{project_path}[/yellow]")

    await rename_project(container, project_path)

    await console.print(container, "[green]Successfully[/green] renamed project")


@interface("Altium Projekt Version ändern", is_altium_project)
async def reversion_altium_project(container: Container):
    project_path = None
    for path in Path.cwd().rglob("*.PRJPCB"):
        project_path = path.parent
        break

    if not project_path:
        await console.print(container, "[red]No Altium project found[/red]")
        return

    await console.print(container, f"Project path: [yellow]{project_path}[/yellow]")

    await update_project_version(container, project_path)

    await console.print(
        container, "[green]Successfully[/green] updated project version"
    )
