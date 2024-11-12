from pathlib import Path, WindowsPath
from typing import Optional


class NetworkPath(WindowsPath):
    """
    Extension of pathlib.WindowsPath that handles network path mapping.
    Automatically tries to find the correct drive letter
    if the network path doesn't exist.
    """

    _network_mappings = {
        "T:": "t_lernende",
        "N:": "n_home-s",
        "S:": "s_mitarbeiter",
        "U:": "u_archiv",
    }

    def __new__(cls, *args, **kwargs):
        # First create the path object
        obj = super().__new__(cls, *args, **kwargs)

        # Store original path and check validity
        obj.original_path = Path(args[0])
        obj.is_valid = obj.exists()

        # If path doesn't exist, try to remap it
        if not obj.is_valid:
            remapped = obj._find_and_remap_path()
            if remapped:
                # Create and return a new NetworkPath with the remapped path
                return NetworkPath(remapped)
            print(
                f"[red]Warning: Could not find valid path for {obj.original_path}[/red]"
            )
            print("[red]Please write to et22seol and ask for help[/red]")

        return obj

    def _find_and_remap_path(self) -> Optional[Path]:
        """
        Attempts to find the correct drive letter by
        searching for the t_lernende folder
        and remaps the path accordingly.

        Returns:
            Optional[Path]: The remapped path if successful, None otherwise
        """
        # Search through all possible drive letters
        drive_letters = [f"{chr(i)}:" for i in range(65, 91)]

        for letter in drive_letters:
            test_path = Path(f"{letter}\\t_lernende")
            if test_path.exists():
                # Found the correct drive, remap the path
                new_path = self._remap_path(letter)
                if new_path and new_path.exists():
                    print(f"Remapped path to: {new_path}")
                    return new_path

        return None

    def _remap_path(self, new_drive: str) -> Optional[Path]:
        """
        Remaps the path to the new drive letter based on the network mapping.

        Args:
            new_drive: The new drive letter to map to (e.g. 'D:')

        Returns:
            Optional[Path]: The remapped path if successful, None otherwise
        """
        original_drive = self.original_path.drive

        if original_drive not in self._network_mappings:
            return None

        network_folder = self._network_mappings[original_drive]
        remaining_path = str(self.original_path).split("\\", 1)[1]

        return Path(f"{new_drive}\\{network_folder}") / remaining_path
