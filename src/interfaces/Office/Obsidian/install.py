import re
import subprocess
import tempfile
from pathlib import Path

import requests

from src.lib.interface import interface
from src.lib.utils import console, safe_download


def extract_obsidian_windows_url(js_content: str) -> str | None:
    pattern = r'Windows:{.*?downloadLink:"(https://.*?\.exe)"'
    match = re.search(pattern, js_content)
    return match.group(1) if match else None


def extract_obsidian_version(js_content: str) -> str | None:
    pattern = r'Windows:{.*?downloadLink:"https://.*?/v([\d.]+)/Obsidian-[\d.]+\.exe"'
    match = re.search(pattern, js_content)
    return match.group(1) if match else None


def get_latest_obsidian_info() -> tuple[str | None, str | None]:
    try:
        response = requests.get("https://obsidian.md/download.js")
        response.raise_for_status()
        content = response.text
        return extract_obsidian_windows_url(content), extract_obsidian_version(content)
    except requests.RequestException as e:
        print(f"Error fetching download.js: {e}")
        return None, None


obsidian_url, obsidian_version = get_latest_obsidian_info()


@interface(f"Obsidian Installieren ({obsidian_version or 'unknown'})")
def install_obsidian():
    if not obsidian_url:
        print("[red]No Obsidian installer found![/red]")
        return

    # create a temporary directory and copy the installer file there
    # this temporary directory will be deleted automatically
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_installer_path = Path(temp_dir) / "Obsidian.exe"

        console.print(f"[green]Downloading Obsidian installer: {obsidian_url}[/green]")
        safe_download(obsidian_url, temp_installer_path)

        console.print(
            f"[green]Running Obsidian installer: {temp_installer_path}[/green]"
        )
        subprocess.run(["cmd", "/c", str(temp_installer_path)])

        console.print("[green]Obsidian installed successfully![/green]")
