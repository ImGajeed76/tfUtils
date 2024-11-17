from pathlib import Path

from textual.containers import Container

from src.lib.interface import interface
from src.lib.paths import NetworkPath
from src.lib.utils import console, safe_copy_file

CHECKLIST_TEMPLATES_PATH = NetworkPath(r"T:\E\LIVE\05_HW_Entwicklung\08_Checklisten")


@interface("Schema-Checkliste erstellen", activate=CHECKLIST_TEMPLATES_PATH.exists)
async def create_schema_checklist(container: Container):
    await _copy_checklist(container, "Checkliste_SCH_v*.docx")


@interface("PCB-Checkliste erstellen", activate=CHECKLIST_TEMPLATES_PATH.exists)
async def create_pcb_checklist(container: Container):
    await _copy_checklist(container, "Checkliste_PCB_v*.docx")


async def _copy_checklist(container: Container, pattern: str):
    checklist_files = list(CHECKLIST_TEMPLATES_PATH.glob(pattern))
    checklist_files.sort()

    if len(checklist_files) == 0:
        await console.print(container, "[red]No checklist file found![/red]")
        return

    checklist_file = checklist_files[-1]

    current_dir = Path().cwd()
    await safe_copy_file(container, checklist_file, current_dir)

    await console.print(container, "[green]Checklist file copied successfully![/green]")
