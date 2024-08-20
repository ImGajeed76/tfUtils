import shutil
import zipfile
from pathlib import Path

from src.lib.interface import interface
from src.lib.paths import OFFICE_PATH
from src.lib.utils import console, safe_copy_file


@interface("Systembeschreibung erstellen")
def create_new_system_description():
    sys_files = list(OFFICE_PATH.glob("Systembeschreibung_Vorlage_v*.dotx"))
    sys_files.sort()

    if len(sys_files) == 0:
        console.print("[red]No Systembeschreibung file found[/red]")
        return

    file = sys_files[-1]

    current_dir = Path().cwd()
    new_file = current_dir / "Systembeschreibung.dotx"
    safe_copy_file(file, new_file)

    console.print(f"[green]Systembeschreibung file copied successfully![/green]")


def systembeschreibung_exists() -> bool:
    sys_files = list(Path().cwd().glob("Systembeschreibung*.dotx"))
    sys_files.sort()

    return len(sys_files) > 0


@interface("Systembeschreibung Bilder exportieren")
def export_system_description_images():
    sys_files = list(Path().cwd().glob("Systembeschreibung*.dotx"))
    sys_files.sort()

    if len(sys_files) == 0:
        console.print("[red]No Systembeschreibung file found[/red]")
        return

    docx = sys_files[-1]

    # Use Path for better cross-platform compatibility
    target_dir = Path.cwd() / "Bilder"
    target_dir.mkdir(exist_ok=True)

    with zipfile.ZipFile(docx, 'r') as docx_zip:
        # Filter for files in the word/media directory
        media_files = [f for f in docx_zip.namelist() if f.startswith('word/media/')]

        # Extract each media file
        for media_file in media_files:
            # Extract the file to a temporary location
            docx_zip.extract(media_file, path=target_dir)

            # Get the filename
            filename = Path(media_file).name

            # Move the file from the temporary nested folder to the output folder
            src = target_dir / 'word' / 'media' / filename
            dst = target_dir / filename

            # If the destination file already exists, remove it
            if dst.exists():
                dst.unlink()

            shutil.move(str(src), str(dst))

    # Clean up the temporary nested folders
    temp_word_folder = target_dir / 'word'
    if temp_word_folder.exists():
        shutil.rmtree(temp_word_folder)

    console.print(f"[green]Images exported successfully to {target_dir}[/green]")