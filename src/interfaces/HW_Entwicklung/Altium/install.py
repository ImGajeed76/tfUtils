import asyncio
import subprocess
import tempfile
from pathlib import Path

from textual.containers import Container

from src.lib.interface import interface
from src.lib.paths import NetworkPath
from src.lib.utils import console, safe_copy_file

ALTIUM_INSTALLER_PATH = NetworkPath(
    r"T:\E\PROGRAMME\02_HW-Entwicklung\AltiumDesigner\AD24"
)


def get_installer_path():
    # get the newest installer file
    installer_files = list(ALTIUM_INSTALLER_PATH.glob("AltiumDesignerSetup*.exe"))
    installer_files.sort()

    return installer_files[-1] if installer_files else None


@interface("Altium Installieren", ALTIUM_INSTALLER_PATH.exists)
async def install_altium(container: Container):
    """
    Installiere Altium Designer.

    ## Inaktiv

    Wenn steht das dieses Interface inaktiv ist,
    dann wurde der Pfad zum Altium Installer nicht gefunden.
    Überprüfen, ob du Zugriff auf das Laufwerk hast.
    """
    installer_path = get_installer_path()

    if not installer_path:
        await console.print(container, "[red]No Altium Designer installer found![/red]")
        return

    # create a temporary directory and copy the installer file there
    # this temporary directory will be deleted automatically
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_installer_path = Path(temp_dir) / installer_path.name
        await safe_copy_file(container, installer_path, temp_installer_path)

        await console.print(
            container,
            f"[green]Running Altium Designer installer: {temp_installer_path}[/green]",
        )

        container.refresh()
        await asyncio.sleep(1)

        subprocess.run(["cmd", "/c", str(temp_installer_path)])
        await console.print(
            container, "[green]Altium Designer installed successfully![/green]"
        )
