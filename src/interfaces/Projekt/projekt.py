import os
from pathlib import Path

from textual.containers import Container

from src.lib.console import ask_input, ask_yes_no
from src.lib.interface import interface
from src.lib.paths import NetworkPath
from src.lib.utils import console, safe_copy_directory

DEFAULT_STRUCT_FOLDER = NetworkPath(
    r"T:\E\LIVE\02_Vorlagen\03_Projektordnerstruktur\EXX-YYY-ZZ_Projektname"
)


@interface("Neue Projektstruktur erstellen", activate=DEFAULT_STRUCT_FOLDER.exists)
async def create_new_project_structure(container: Container):
    from src.interfaces.HW_Entwicklung.Altium.altium import new_altium_project
    from src.interfaces.Office.Checkliste.checkliste import (
        create_pcb_checklist,
        create_schema_checklist,
    )
    from src.interfaces.Office.Obsidian.obsidian import create_new_obsidian_vault
    from src.interfaces.Office.Systembeschreibung.systembeschreibung import (
        create_new_system_description,
    )

    original_wd = Path().cwd()

    try:
        project_folder_name = await ask_input(
            container,
            "Wie soll der Projektordner heißen?\n"
            "Der Projektname muss das Format 'EXX-YYY-ZZ_Projectname' haben.\n"
            "(ZZ sind zwei grosse Buchstaben)",
            regex=r"^E\d{2}-\d{3}-[A-Z]{2}_[A-Za-z0-9]+$",
        )
        project_name = project_folder_name.split("_")[-1]

        base_dir = Path().cwd()
        project_dir = base_dir / project_folder_name

        if project_dir.exists():
            await console.print(
                container, "[red]Projektordner existiert bereits![/red]"
            )
            return

        project_dir.mkdir()

        await safe_copy_directory(container, DEFAULT_STRUCT_FOLDER, project_dir)

        await console.print(container, "[green]Projekt erfolgreich erstellt![/green]")

        # ------ SCHEMA LAYOUT ------
        await console.print(container, "-" * 50)

        sl_dir = project_dir / "Hardware" / "SCH_PCB"

        if await ask_yes_no(
            container,
            "Möchten Sie ein Schema Layout im neuen Projekt erstellen?",
        ):
            os.chdir(sl_dir)

            sl_connection = sl_dir / "02_Vorlage_Schema_Layout - Verknüpfung.lnk"
            if sl_connection.exists():
                sl_connection.unlink()

            await new_altium_project(container, project_name, True)

        # ------ Checklist ------
        await console.print(container, "-" * 50)

        checklist_dir = project_dir / "Hardware" / "SCH_PCB"

        if await ask_yes_no(
            container, "Möchten Sie Checklisten im neuen Projekt erstellen?"
        ):
            os.chdir(checklist_dir)

            checklist_connection = checklist_dir / "08_Checklisten - Verknüpfung.lnk"
            if checklist_connection.exists():
                checklist_connection.unlink()

            await create_schema_checklist(container)
            await create_pcb_checklist(container)

        # ------ Obsidian Vault ------
        await console.print(container, "-" * 50)

        obsidian_dir = project_dir / "Journal"

        if await ask_yes_no(
            container,
            "Möchten Sie einen Obsidian Vault im neuen Projekt erstellen?",
        ):
            os.chdir(obsidian_dir)

            await create_new_obsidian_vault(container)

        # ------ Systembeschreibung ------
        await console.print(container, "-" * 50)

        sys_desc_dir = project_dir / "Systembeschreibung"

        if await ask_yes_no(
            container,
            "Möchten Sie eine Systembeschreibung im neuen Projekt erstellen?",
        ):
            os.chdir(sys_desc_dir)

            sys_link = sys_desc_dir / "01_Office - Verknüpfung.lnk"
            if sys_link.exists():
                sys_link.unlink()

            await create_new_system_description(container)

        await console.print(container, "-" * 50)

        await console.print(
            container, "[green]Alle Schritte erfolgreich abgeschlossen![/green]"
        )
    finally:
        os.chdir(original_wd)
