import subprocess
import tempfile
from pathlib import Path

from src.lib.interface import interface
from src.lib.paths import NetworkPath
from src.lib.utils import console, safe_copy_file

ALTIUM_INSTALLER_PATH = NetworkPath(
    r"Z:\t_lernende\E\PROGRAMME\02_HW-Entwicklung\AltiumDesigner\AD24"
)


def get_installer_path():
    # get the newest installer file
    installer_files = list(ALTIUM_INSTALLER_PATH.glob("AltiumDesignerSetup*.exe"))
    installer_files.sort()

    return installer_files[-1] if installer_files else None


@interface("Altium Installieren")
def install_altium():
    installer_path = get_installer_path()

    if not installer_path:
        console.print("[red]No Altium Designer installer found![/red]")
        return

    # create a temporary directory and copy the installer file there
    # this temporary directory will be deleted automatically
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_installer_path = Path(temp_dir) / installer_path.name
        safe_copy_file(installer_path, temp_installer_path)

        console.print(
            f"[green]Running Altium Designer installer: {temp_installer_path}[/green]"
        )
        subprocess.run(["cmd", "/c", str(temp_installer_path)])
        console.print("[green]Altium Designer installed successfully![/green]")
