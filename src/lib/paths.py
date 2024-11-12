import os
import sys
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
        try:
            # Handle different Python versions
            if sys.version_info >= (3, 12):
                # Python 3.12+ initialization
                temp_path = WindowsPath(*args)
                obj = WindowsPath.__new__(cls, str(temp_path))
            else:
                # Pre-Python 3.12 initialization
                obj = WindowsPath.__new__(cls, *args)

            # Store original path in a way that works for both versions
            obj._original_path = str(args[0]) if args else ""

            # Check if path exists without using pathlib's exists()
            try:
                obj._is_valid = os.path.exists(str(obj))
            except Exception:
                obj._is_valid = False

            # If path doesn't exist, try to remap it
            if not obj._is_valid:
                remapped = obj._find_and_remap_path()
                if remapped:
                    # Create new WindowsPath with remapped path and
                    # copy over our custom attributes
                    if sys.version_info >= (3, 12):
                        new_obj = WindowsPath.__new__(cls, str(remapped))
                    else:
                        new_obj = WindowsPath.__new__(cls, remapped)
                    new_obj._original_path = obj._original_path
                    new_obj._is_valid = True
                    print(f"Remapped path to: {remapped}")
                    return new_obj
                print(f"Warning: Could not find valid path for {obj._original_path}")
                print("Please write to et22seol and ask for help")

            return obj

        except Exception as e:
            # Fallback to creating a regular WindowsPath if something goes wrong
            print(f"Warning: Error creating NetworkPath: {e}")
            return WindowsPath(*args)

    @property
    def original_path(self):
        """Safe access to original path"""
        return Path(self._original_path)

    @property
    def is_valid(self):
        """Safe access to validity status"""
        return getattr(self, "_is_valid", False)

    def _find_and_remap_path(self) -> Optional[Path]:
        """
        Attempts to find the correct drive letter by
        searching for the t_lernende folder
        and remaps the path accordingly.

        Returns:
            Optional[Path]: The remapped path if successful, None otherwise
        """
        # Search through all possible drive letters
        drive_letters = [f"{chr(i)}:" for i in range(65, 91)]  # A: through Z:

        for letter in drive_letters:
            test_path = os.path.join(letter, "t_lernende")
            try:
                if os.path.exists(test_path):
                    # Found the correct drive, remap the path
                    new_path = self._remap_path(letter)
                    if new_path and os.path.exists(str(new_path)):
                        return new_path
            except Exception:
                continue

        return None

    def _remap_path(self, new_drive: str) -> Optional[Path]:
        """
        Remaps the path to the new drive letter based on the network mapping.

        Args:
            new_drive: The new drive letter to map to (e.g. 'D:')

        Returns:
            Optional[Path]: The remapped path if successful, None otherwise
        """
        try:
            # Get original drive in a version-compatible way
            original_path_str = str(self._original_path)
            original_drive = (
                original_path_str[:2] if len(original_path_str) >= 2 else ""
            )

            if original_drive not in self._network_mappings:
                return None

            network_folder = self._network_mappings[original_drive]

            # Split path in a way that works for both versions
            parts = original_path_str.split("\\", 1)
            remaining_path = parts[1] if len(parts) > 1 else ""

            new_path = Path(f"{new_drive}\\{network_folder}") / remaining_path
            return new_path
        except Exception as e:
            print(f"Error in _remap_path: {e}")
            return None
