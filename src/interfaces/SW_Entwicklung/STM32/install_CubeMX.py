import subprocess
import tempfile
from pathlib import Path

from src.lib.interface import interface
from src.lib.paths import NetworkPath
from src.lib.utils import console, safe_copy_file

CUBEMX_INSTALLER_DIR = NetworkPath(
    r"X:\t_lernende\E\PROGRAMME\01_SW-Entwicklung\ST\STM32CubeMX\SetupSTM32CubeMX-6.2.1-Win.exe"
)

print(CUBEMX_INSTALLER_DIR)


@interface("STM32CubeMX Installieren")
def install_cubemx():
    if not CUBEMX_INSTALLER_DIR:
        console.print("[red]Keine CubeMX Instalations Datei gefunden![/red]")
        return

    # create a temporary directory and copy the installer file there
    # this temporary directory will be deleted automatically
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create the full path for the executable in the temp directory
        temp_installer_path = Path(temp_dir) / "SetupSTM32CubeMX.exe"

        # Copy the installer to temporary location
        safe_copy_file(CUBEMX_INSTALLER_DIR, temp_installer_path)

        console.print(
            f"[green]STM32CubeMX Installer ausführen: {temp_installer_path}[/green]"
        )
        # Run the executable directly
        subprocess.run(["cmd", "/c", str(temp_installer_path)])
        console.print("[green]STM32CubeMX wurde erfolgreich instaliert![/green]")
