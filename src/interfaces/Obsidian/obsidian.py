from pathlib import Path

from src.lib.console import ask_input
from src.lib.interface import interface
from src.lib.utils import console, safe_copy_directory


@interface("Neuen Obsidian Vault erstellen")
def create_new_obsidian_vault():
    vault_name = ask_input("Vault Name", "Wie soll dein neuer Vault heißen?")

    # create the vault directory
    base_dir = Path().cwd()
    vault_dir = base_dir / vault_name

    if vault_dir.exists():
        console.print(f"[red]Vault directory already exists![/red]")
        return

    vault_dir.mkdir()

    current_dir = Path(__file__).parent

    obsidian_template_dir = current_dir / "ObsidianTemplate"

    safe_copy_directory(obsidian_template_dir, vault_dir)

    console.print(f"[green]Vault created successfully![/green]")
