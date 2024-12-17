import os
import subprocess
import sys
from pathlib import Path


def is_running_in_powershell():
    """Check if the script is running in PowerShell"""
    # Check for PowerShell-specific environment variables
    return any(
        env_var in os.environ
        for env_var in ["PSModulePath", "PSExecutionPolicyPreference"]
    )


def restart_in_powershell():
    """Restart the current script in PowerShell"""
    script_path = sys.argv[0]
    args = sys.argv[1:]

    # Construct the PowerShell command
    powershell_cmd = [
        "powershell.exe",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        f'& python "{script_path}" {" ".join(args)}',
    ]

    # Start PowerShell process
    try:
        process = subprocess.run(powershell_cmd, check=True)
        sys.exit(process.returncode)
    except subprocess.CalledProcessError as e:
        print(f"Error launching PowerShell: {e}")
        sys.exit(1)


def get_application_path():
    """Get the application base path whether running as script or frozen exe"""
    if getattr(sys, "frozen", False):
        # If the application is run as a bundle (pyinstaller)
        return Path(sys._MEIPASS)
    else:
        # If the application is run from a Python interpreter
        return Path(__file__).parent


def main():
    # Check if running on Windows and not in PowerShell
    if sys.platform == "win32" and not is_running_in_powershell():
        restart_in_powershell()
        return

    # Get the base path
    base_path = get_application_path()

    # Import the modules after setting up the path
    from src.lib.interface_loader import (
        create_folder_references,
        create_interface_references,
        scan_interfaces,
    )
    from src.lib.interface_viewer import InterfaceViewer

    # Construct paths relative to the application base path
    interface_folder = base_path / "src" / "interfaces"
    src_folder = base_path / "src"

    # Ensure the paths exist and are accessible
    if not interface_folder.exists():
        print(f"Error: Interface folder not found at {interface_folder}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Base path: {base_path}")
        sys.exit(1)

    interfaces = scan_interfaces(interface_folder, src_folder)
    references = create_interface_references(interfaces)
    references.extend(create_folder_references(interfaces, interface_folder))
    references.sort()

    app = InterfaceViewer("TF Utils", references)
    app.run()
    sys.exit(app.return_code or 0)


if __name__ == "__main__":
    main()
