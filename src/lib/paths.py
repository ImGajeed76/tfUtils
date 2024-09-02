from pathlib import Path

from src.lib.utils import console

PATHS = {
    "U_VISION_TEMPLATES_PATH": Path(r"T:\E\LIVE\06_SW_Entwicklung\11_Vorlagen"),
    "ALTIUM_TEMPLATES_PATH": Path(r"T:\E\LIVE\05_HW_Entwicklung\02_Vorlage_Schema_Layout"),
    "CHECKLIST_TEMPLATES_PATH": Path(r"T:\E\LIVE\05_HW_Entwicklung\08_Checklisten"),
    "DEFAULT_STRUCT_FOLDER": Path(r"T:\E\LIVE\02_Vorlagen\03_Projektordnerstruktur\EXX-YYY-ZZ_Projektname"),
    "OFFICE_PATH": Path(r"T:\E\LIVE\02_Vorlagen\01_Office")
}


def check_paths() -> bool:
    all_good = True

    # check if the first path exists.
    if not PATHS["U_VISION_TEMPLATES_PATH"].exists():
        # find the correct drive by searching for a drive with the folder `t_lernende` in it
        drive_letters = [f"{chr(i)}:" for i in range(65, 91)]
        for letter in drive_letters:
            path = Path(f"{letter}\\t_lernende")
            if path.exists():
                # change all paths to the correct drive. e.g. with D
                # T:\... -> D:\t_lernende\...
                # N:\... -> D:\n_home-s\...
                # S:\... -> D:\s_mitarbeiter\...
                # U:\... -> D:\u_archiv\...

                for key in PATHS.keys():
                    wrong_drive = PATHS[key].drive
                    correct_path = Path(f"{letter}\\{wrong_drive[0].lower()}_archiv") / str(PATHS[key]).replace(f"{wrong_drive}:", "")
                    PATHS[key] = correct_path
                console.print(f"Changed paths to {letter}")

    for path in PATHS.values():
        if not path.exists():
            console.print(f"[red]Error: {path} does not exist![/red]")
            all_good = False

    if not all_good:
        console.print("[red]Paths are not correct or have changed![/red]")
        console.print("[red]Please write to et22seol and ask for help[/red]")

    return all_good
