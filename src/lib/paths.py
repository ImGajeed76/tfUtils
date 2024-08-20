from pathlib import Path

from src.lib.utils import console

U_VISION_TEMPLATES_PATH = Path(r"T:\E\LIVE\06_SW_Entwicklung\11_Vorlagen")
ALTIUM_TEMPLATES_PATH = Path(r"T:\E\LIVE\05_HW_Entwicklung\02_Vorlage_Schema_Layout")
CHECKLIST_TEMPLATES_PATH = Path(r"T:\E\LIVE\05_HW_Entwicklung\08_Checklisten")
DEFAULT_STRUCT_FOLDER = Path(r"T:\E\LIVE\02_Vorlagen\03_Projektordnerstruktur\EXX-YYY-ZZ_Projektname")
OFFICE_PATH =  Path(r"T:\E\LIVE\02_Vorlagen\01_Office")

def check_paths() -> bool:
    paths: list[Path] = [
        U_VISION_TEMPLATES_PATH,
        ALTIUM_TEMPLATES_PATH,
        CHECKLIST_TEMPLATES_PATH,
        DEFAULT_STRUCT_FOLDER,
        OFFICE_PATH
    ]
    all_good = True

    for path in paths:
        if not path.exists():
            console.print(f"[red]Error: {path} does not exist![/red]")
            all_good = False

    if not all_good:
        console.print("[red]Paths are not correct or have changed![/red]")
        console.print("[red]Please write to et22seol and ask for help[/red]")

    return all_good