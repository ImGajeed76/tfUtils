import shutil
import zipfile
from pathlib import Path

from textual.containers import Container

from src.lib.interface import interface
from src.lib.paths import NetworkPath
from src.lib.utils import console, safe_copy_file

OFFICE_PATH = NetworkPath(r"T:\E\LIVE\02_Vorlagen\01_Office")


@interface("Systembeschreibung erstellen", activate=OFFICE_PATH.exists)
async def create_new_system_description(container: Container):
    sys_files = list(OFFICE_PATH.glob("Systembeschreibung_Vorlage_v*.dotx"))
    sys_files.sort()

    if len(sys_files) == 0:
        await console.print(container, "[red]No Systembeschreibung file found[/red]")
        return

    file = sys_files[-1]

    current_dir = Path().cwd()
    new_file = current_dir / "Systembeschreibung.docx"
    await safe_copy_file(container, file, new_file)

    await console.print(
        container, "[green]Systembeschreibung file copied successfully![/green]"
    )


def systembeschreibung_exists() -> bool:
    sys_files = list(Path().cwd().glob("Systembeschreibung*.docx"))
    sys_files.sort()

    return len(sys_files) > 0


@interface("Systembeschreibung Bilder exportieren", activate=systembeschreibung_exists)
async def export_system_description_images(container: Container):
    sys_files = list(Path().cwd().glob("Systembeschreibung*.docx"))
    sys_files.sort()

    if len(sys_files) == 0:
        await console.print(container, "[red]No Systembeschreibung file found[/red]")
        return

    docx = sys_files[-1]

    # Use Path for better cross-platform compatibility
    target_dir = Path.cwd() / "Bilder"
    target_dir.mkdir(exist_ok=True)

    with zipfile.ZipFile(docx, "r") as docx_zip:
        # Filter for files in the word/media directory
        media_files = [f for f in docx_zip.namelist() if f.startswith("word/media/")]

        # Extract each media file
        for media_file in media_files:
            # Extract the file to a temporary location
            docx_zip.extract(media_file, path=target_dir)

            # Get the filename
            filename = Path(media_file).name

            # Move the file from the temporary nested folder to the output folder
            src = target_dir / "word" / "media" / filename
            dst = target_dir / filename

            # If the destination file already exists, remove it
            if dst.exists():
                dst.unlink()

            shutil.move(str(src), str(dst))

    # Clean up the temporary nested folders
    temp_word_folder = target_dir / "word"
    if temp_word_folder.exists():
        shutil.rmtree(temp_word_folder)

    await console.print(
        container, f"[green]Images exported successfully to {target_dir}[/green]"
    )
