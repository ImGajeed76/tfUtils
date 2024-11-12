from pathlib import Path

from src.lib.interface import interface
from src.lib.paths import NetworkPath
from src.lib.utils import console, safe_copy_file

CHECKLIST_TEMPLATES_PATH = NetworkPath(r"T:\E\LIVE\05_HW_Entwicklung\08_Checklisten")


@interface("Schema-Checkliste erstellen")
def create_schema_checklist():
    _copy_checklist("Checkliste_SCH_v*.docx")


@interface("PCB-Checkliste erstellen")
def create_pcb_checklist():
    _copy_checklist("Checkliste_PCB_v*.docx")


def _copy_checklist(pattern: str):
    checklist_files = list(CHECKLIST_TEMPLATES_PATH.glob(pattern))
    checklist_files.sort()

    if len(checklist_files) == 0:
        console.print("[red]No checklist file found![/red]")
        return

    checklist_file = checklist_files[-1]

    current_dir = Path().cwd()
    safe_copy_file(checklist_file, current_dir)

    console.print("[green]Checklist file copied successfully![/green]")
