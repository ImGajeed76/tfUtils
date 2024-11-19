import asyncio
import subprocess
import tempfile
import zipfile
from pathlib import Path

from textual.containers import Container

from src.lib.interface import interface
from src.lib.paths import NetworkPath
from src.lib.utils import console, safe_copy_file

UVISION_INSTALLER_DIR = NetworkPath(
    r"T:\E\PROGRAMME\01_SW-Entwicklung\Keil_uV5_Developement-Package\Keil_uV5_Developement-Package.zip"
)


@interface("uVision Installieren", UVISION_INSTALLER_DIR.exists)
async def install_uvision(container: Container):
    if not UVISION_INSTALLER_DIR:
        await console.print(
            container, "[red]Keinen uVision Instalations Ortner gefunden![/red]"
        )
        container.scroll_end()
        return

    # Store the TemporaryDirectory instance
    temp_dir = tempfile.TemporaryDirectory()
    try:
        temp_installer_zip_path = Path(temp_dir.name) / "uvison.zip"
        temp_installer_path = Path(temp_dir.name) / "uvison"
        await safe_copy_file(container, UVISION_INSTALLER_DIR, temp_installer_zip_path)

        with zipfile.ZipFile(temp_installer_zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_installer_path)

        installer_path = (
            temp_installer_path
            / "Keil_uV5_Developement-Package"
            / "uV5_Installation.bat"
        )

        await console.print(
            container,
            f"[green]"
            f"uVision Installer wird in neuem Fenster geöffnet: {installer_path}"
            f"[/green]",
        )

        await console.print(
            container,
            "[yellow]Bitte folgen Sie den Anweisungen im neuen Fenster.[/yellow]",
        )

        await console.print(
            container,
            "[yellow]Schliessen sie das andere Fester wenn sie fertig sind![/yellow]",
        )

        container.refresh()
        await asyncio.sleep(1)

        # Open in new window using cmd /c start and wait for it to complete
        process = subprocess.Popen(
            ["cmd", "/c", "start", "/wait", "cmd", "/k", str(installer_path)],
            cwd=str(installer_path.parent),
        )

        # Wait for the process to complete
        process.wait()

        await console.print(container, "[green]Installation abgeschlossen.[/green]")

    finally:
        # Clean up the temporary directory after installation is complete
        temp_dir.cleanup()
