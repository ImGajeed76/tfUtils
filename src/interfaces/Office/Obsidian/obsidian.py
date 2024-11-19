from pathlib import Path

from textual.containers import Container

from src.lib.console import ask_input
from src.lib.interface import interface
from src.lib.utils import console, safe_copy_directory


@interface("Neuen Obsidian Vault erstellen")
async def create_new_obsidian_vault(container: Container):
    """
    Erstelle einen neuen Obsidian Vault.

    Dieses Interface erstellt einen neuen Obsidian Vault im aktuellen Verzeichnis.
    Dieser neue Vault enthält bereits grundlegende Einstellungen und Plugins für
    eine bessere Obsidian-Erfahrung.

    ## Plugin Liste:
    - Excalidraw
    - Numerals
    - Better Word Count
    - OZ Calendar
    - Obsidian Banners
    - Obsidian File Cleaner
    - Quick Add
    - Table Editor
    - Code Block Customizer
    """
    vault_name = await ask_input(
        container, "Wie soll dein neuer Vault heißen?", regex="^[a-zA-Z0-9_-]+$"
    )

    # create the vault directory
    base_dir = Path().cwd()
    vault_dir = base_dir / vault_name

    if vault_dir.exists():
        await console.print(container, "[red]Vault directory already exists![/red]")
        return

    vault_dir.mkdir()

    current_dir = Path(__file__).parent

    obsidian_template_dir = current_dir / "ObsidianTemplate"

    await safe_copy_directory(container, obsidian_template_dir, vault_dir)

    await console.print(container, "[green]Vault created successfully![/green]")
