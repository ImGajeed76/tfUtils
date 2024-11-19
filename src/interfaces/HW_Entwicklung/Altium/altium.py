import getpass
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

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
    """
    Dieses Interface erstellt ein neues Altium Projekt aus einer Vorlage.
    Es ändert den Projektnamen und die Projektversion und
    fügt eine Versionshistorie hinzu.

    ## Inaktiv:

    Wenn steht das dieses Interface inaktiv ist,
    dann wurde der Pfad zu den Altium Vorlagen nicht gefunden.
    Überprüfen, ob du Zugriff auf das Laufwerk hast.
    """
    if default_name is None:
        default_name = Path.cwd().name

    template_paths = get_all_schema_layout_templates()

    # sort the templates by path
    template_paths.sort()

    template_names = [
        str(path.relative_to(ALTIUM_TEMPLATES_PATH)) for path in template_paths
    ]

    template_name = await ask_select(
        container, "Wähle die Altium Projektvorlage aus", options=template_names
    )

    template_path = ALTIUM_TEMPLATES_PATH / template_name

    project_name = await ask_input(
        container,
        "Was ist der Name deines Altium Projekts",
        placeholder=default_name,
        regex=r"^[a-zA-Z0-9-]+$",
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
        f"Die Vorlage wurde [green]erfolgreich[/green] "
        f"nach [yellow]{project_path}[/yellow] kopiert",
    )

    # Run post-copy operations
    await _update_project_vc(project_path)
    await update_project_version(container, project_path, "V1.0")
    await rename_project(container, project_path, project_name)

    await console.print(
        container,
        "Die Projektversion wurde [green]erfolgreich[/green] aktualisiert "
        "und das Projekt wurde [green]erfolgreich[/green] umbenannt.",
    )

    await console.print(
        container,
        "Altium Projekt wurde [green]erfolgreich[/green] erstellt. "
        "Du kannst TF-Utils jetzt schließen.",
    )


async def _update_project_vc(project_path: Path):
    project_file = next(project_path.glob("*.PRJPCB"))
    project_name, project_version = project_file.stem.split("_")

    # find all files that contain the project name
    project_files = list(project_path.rglob(f"*{project_name}*{project_version}*"))

    # create a replacement dictionary
    replacements = {}
    for file in project_files:
        replacements[file] = file.with_name(
            file.name.replace(project_name, "{project_name}").replace(
                project_version, "{project_version}"
            )
        )

    replacements_to_root = {}
    for file, new_file in replacements.items():
        new_file = new_file.relative_to(project_path)
        file = file.relative_to(project_path)

        # Skip history files
        if str(file).startswith("History"):
            continue

        replacements_to_root[str(file.as_posix())] = str(new_file.as_posix())

    vc_data = {"project_name": project_name, "replacements": replacements_to_root}

    vc_file = project_path / ".vc.json"
    with open(vc_file, "w") as f:
        json.dump(vc_data, f)


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
            "Die neue Versionsnummer setzt sich wie folgt zusammen:\n"
            "[yellow]x[/yellow].[magenta]y[/magenta]\n"
            "| |\n"
            "| +------- [magenta]Nebenversion[/magenta] "
            "(Erweiterungen & Fehlerbehebungen)\n"
            "+--------- [yellow]Hauptversion[/yellow] "
            "(Neustart / grundlegende Änderung / keine Rückwärtskompatibilität)\n"
            "\n"
            f"Aktuelle Projektversion: "
            f"{old_project_version_major}.{old_project_version_minor}\n"
        )

        regex = (
            rf"^(?:"
            rf"(?:{old_project_version_major + 1}\.\d+)|"
            rf"(?:{old_project_version_major}\."
            rf"(?:[{old_project_version_minor + 1}-9]|\d{{2,}}))"
            rf")$"
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
            "Was ist der Grund für diese Änderung?",
            placeholder="Initial Project Creation",
            regex=r"^[a-zA-Z0-9-]+$",
        )

    else:
        new_project_version = version
        comment = "Initial Project Creation"

    # Get user initials
    user = getpass.getuser().split("\\")[-1][-4:]
    user = await ask_input(
        container, "Dein Kürzel", placeholder=user, regex=r"^[a-zA-Z0-9-]+$"
    )

    # Get current date
    date = datetime.now().strftime("%m/%d/%Y")

    # Rename files
    _rename_files(
        project_path,
        new_project_version,
        project_name,
    )

    # Edit project files
    _edit_project_files(
        project_path,
        new_project_version,
        project_name,
    )

    await _update_project_vc(project_path)

    # Update history file
    history_line = f"{new_project_version[1:]}\t\t{user}\t{date}\t{comment}"
    with open("_history.txt", "a") as f:
        f.write(history_line + "\n")

    await console.print(
        container,
        "Die Projektversion wurde [green]erfolgreich[/green] aktualisiert.\n",
    )


async def rename_project(
    container: Container, project_path: Path, new_project_name=None
):
    os.chdir(project_path)

    # Extract old project name and version
    old_filename = next(Path.cwd().glob("*.PRJPCB")).stem
    old_project_name, project_version = old_filename.split("_")

    # Display old project name
    await console.print(container, f"Alter Projektname: {old_project_name}")

    # Get new project name
    if not new_project_name:
        new_project_name = await ask_input(
            container,
            f"Wie soll das Projekt heißen? "
            f"[yellow](Alter Projektname: {old_project_name})[/yellow]",
            regex=r"^[a-zA-Z0-9-]+$",
        )

    # Rename files
    _rename_files(
        project_path,
        project_version,
        new_project_name,
    )

    # Edit project files
    _edit_project_files(
        project_path,
        project_version,
        new_project_name,
    )

    await _update_project_vc(project_path)

    await console.print(
        container, "Das Projekt wurde [green]erfolgreich[/green] umbenannt."
    )


def _load_file_mappings(
    project_path: Path,
    new_project_name: str,
    new_version: str,
) -> List[Tuple[str, str]]:
    vc_file = project_path / ".vc.json"
    with open(vc_file) as f:
        vc_data = json.load(f)

    return [
        (
            str(old),
            str(new)
            .replace("{project_name}", new_project_name)
            .replace("{project_version}", new_version),
        )
        for old, new in vc_data["replacements"].items()
    ]


def _rename_files(
    project_path: Path,
    new_version,
    new_project_name,
):
    file_mappings = _load_file_mappings(project_path, new_project_name, new_version)

    for old_path, new_path in file_mappings:
        old_full_path = project_path / old_path
        new_full_path = project_path / new_path
        if old_full_path.exists():
            old_full_path.rename(new_full_path)


def _edit_project_files(
    project_path: Path,
    new_version,
    new_project_name,
):
    file_paths = [
        f"{new_project_name}_{new_version}.PRJPCB",
        f"{new_project_name}_{new_version}.OutJob",
    ]

    file_mappings = _load_file_mappings(project_path, new_project_name, new_version)

    replacements = [
        (str(Path(old).stem), str(Path(new).stem)) for old, new in file_mappings
    ]

    for file_path in file_paths:
        full_path = project_path / file_path
        if full_path.exists():
            with open(full_path) as file:
                content = file.read()

            for old, new in replacements:
                content = content.replace(old, new)

            with open(full_path, "w") as file:
                file.write(content)


def is_altium_project() -> bool:
    return any(file.suffix in (".PRJPCB") for file in Path.cwd().rglob("*.PRJPCB"))


@interface("Altium Projekt umbenennen", is_altium_project)
async def rename_altium_project(container: Container):
    """
    Dieses Interface benennt das Altium Projekt um.

    ## Inaktiv:

    Wenn steht das dieses Interface inaktiv ist,
    dann wurde kein Altium Projekt gefunden.
    Überprüfen, ob du dich im richtigen Ordner befindest.

    ## Tipp:

    Du siehst den aktuellen Pfad oben in der Kopfleiste.
    """
    project_path = None
    for path in Path.cwd().rglob("*.PRJPCB"):
        project_path = path.parent
        break

    if not project_path:
        await console.print(container, "[red]Kein Altium Projekt gefunden[/red]")
        return

    await console.print(container, f"Projekt pfad: [yellow]{project_path}[/yellow]")

    await rename_project(container, project_path)

    await console.print(container, "[green]Erfolgreich[/green] umbenannt")


@interface("Altium Projekt Version ändern", is_altium_project)
async def reversion_altium_project(container: Container):
    """
    Dieses Interface ändert die Version des Altium Projekts.

    ## Inaktiv:

    Wenn steht das dieses Interface inaktiv ist,
    dann wurde kein Altium Projekt gefunden.
    Überprüfen, ob du dich im richtigen Ordner befindest.

    ## Tipp:

    Du siehst den aktuellen Pfad oben in der Kopfleiste.
    """
    project_path = None
    for path in Path.cwd().rglob("*.PRJPCB"):
        project_path = path.parent
        break

    if not project_path:
        await console.print(container, "[red]Kein Altium Projekt gefunden[/red]")
        return

    await console.print(container, f"Projekt pfad: [yellow]{project_path}[/yellow]")

    await update_project_version(container, project_path)

    await console.print(
        container, "Projektversion wurde [green]erfolgreich[/green] aktualisiert."
    )
