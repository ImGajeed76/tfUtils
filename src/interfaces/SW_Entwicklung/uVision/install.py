import subprocess
import tempfile
import zipfile
from pathlib import Path

from src.lib.interface import interface
from src.lib.paths import NetworkPath
from src.lib.utils import console, safe_copy_file

UVISION_INSTALLER_DIR = NetworkPath(
    r"T:\E\PROGRAMME\01_SW-Entwicklung\Keil_uV5_Developement-Package\Keil_uV5_Developement-Package.zip"
)

print(UVISION_INSTALLER_DIR)


@interface("uVision Installieren")
def install_uvision():
    if not UVISION_INSTALLER_DIR:
        console.print("[red]Keinen uVision Instalations Ortner gefunden![/red]")
        return

    # create a temporary directory and copy the installer file there
    # this temporary directory will be deleted automatically
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_installer_zip_path = Path(temp_dir) / "uvison.zip"
        temp_installer_path = Path(temp_dir) / "uvison"
        safe_copy_file(UVISION_INSTALLER_DIR, temp_installer_zip_path)

        with zipfile.ZipFile(temp_installer_zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_installer_path)

        installer_path = (
            temp_installer_path
            / "Keil_uV5_Developement-Package"
            / "uV5_Installation.bat"
        )

        console.print(f"[green]uVision Installer ausführen: {installer_path}[/green]")
        subprocess.run(str(installer_path), shell=True, cwd=installer_path.parent)
        console.print("[green]uVision wurde erfolgreich instaliert![/green]")
