import os
from pathlib import Path

from src.lib.console import ask_input, ask_yes_no
from src.lib.interface import interface
from src.lib.paths import NetworkPath
from src.lib.utils import console, safe_copy_directory

DEFAULT_STRUCT_FOLDER = NetworkPath(
    r"T:\E\LIVE\02_Vorlagen\03_Projektordnerstruktur\EXX-YYY-ZZ_Projektname"
)


@interface("Neue Projektstruktur erstellen", activate=DEFAULT_STRUCT_FOLDER.is_valid)
def create_new_project_structure():
    from src.interfaces.Altium.altium import new_altium_project
    from src.interfaces.Obsidian.obsidian import create_new_obsidian_vault
    from src.interfaces.Office.Checkliste.checkliste import (
        create_pcb_checklist,
        create_schema_checklist,
    )
    from src.interfaces.Office.Systembeschreibung.systembeschreibung import (
        create_new_system_description,
    )

    project_folder_name = ask_input(
        "Projektordnername",
        "Wie soll der Projektordner heißen?\n"
        "Der Projektname muss das Format 'EXX-YYY-ZZ_Projectname' haben.\n"
        "(ZZ sind zwei grosse Buchstaben)",
        regex=r"^E\d{2}-\d{3}-[A-Z]{2}_[A-Za-z0-9]+$",
    )
    project_name = project_folder_name.split("_")[-1]

    base_dir = Path().cwd()
    project_dir = base_dir / project_folder_name

    if project_dir.exists():
        console.print("[red]Projektordner existiert bereits![/red]")
        return

    project_dir.mkdir()

    safe_copy_directory(DEFAULT_STRUCT_FOLDER, project_dir)

    console.print("[green]Projekt erfolgreich erstellt![/green]")

    # ------ SCHEMA LAYOUT ------
    console.print("-" * 50)

    sl_dir = project_dir / "Hardware" / "SCH_PCB"

    if ask_yes_no(
        "Schema Layout erstellen",
        "Möchten Sie ein Schema Layout im neuen Projekt erstellen?",
    ):
        os.chdir(sl_dir)

        sl_connection = sl_dir / "02_Vorlage_Schema_Layout - Verknüpfung.lnk"
        if sl_connection.exists():
            sl_connection.unlink()

        console.clear()
        new_altium_project(project_name, True)
        console.clear()

    # ------ Checklist ------
    console.print("-" * 50)

    checklist_dir = project_dir / "Hardware" / "SCH_PCB"

    if ask_yes_no(
        "Checklisten erstellen", "Möchten Sie Checklisten im neuen Projekt erstellen?"
    ):
        os.chdir(checklist_dir)

        checklist_connection = checklist_dir / "08_Checklisten - Verknüpfung.lnk"
        if checklist_connection.exists():
            checklist_connection.unlink()

        create_schema_checklist()
        create_pcb_checklist()
        console.clear()

    # ------ Obsidian Vault ------
    console.print("-" * 50)

    obsidian_dir = project_dir / "Journal"

    if ask_yes_no(
        "Obsidian Vault erstellen",
        "Möchten Sie einen Obsidian Vault im neuen Projekt erstellen?",
    ):
        os.chdir(obsidian_dir)

        console.clear()
        create_new_obsidian_vault()
        console.clear()

    # ------ Systembeschreibung ------
    console.print("-" * 50)

    sys_desc_dir = project_dir / "Systembeschreibung"

    if ask_yes_no(
        "Systembeschreibung erstellen",
        "Möchten Sie eine Systembeschreibung im neuen Projekt erstellen?",
    ):
        os.chdir(sys_desc_dir)

        sys_link = sys_desc_dir / "01_Office - Verknüpfung.lnk"
        if sys_link.exists():
            sys_link.unlink()

        create_new_system_description()
        console.clear()
