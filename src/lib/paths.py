from pathlib import WindowsPath


class ValidatedWindowsPath(WindowsPath):
    """A WindowsPath that knows if it's valid."""

    def __new__(cls, *args, is_valid: bool = False, **kwargs):
        self = super().__new__(cls, *args, **kwargs)
        self._is_valid = is_valid
        return self

    @property
    def is_valid(self) -> bool:
        return self._is_valid


class NetworkPath:
    """
    Factory class that creates ValidatedWindowsPath objects with
    automatic network path mapping.
    """

    _network_mappings = {
        "T:": "t_lernende",
        "N:": "n_home-s",
        "S:": "s_mitarbeiter",
        "U:": "u_archiv",
    }

    def __new__(cls, path_str: str) -> ValidatedWindowsPath:
        # Create initial path
        path = ValidatedWindowsPath(path_str)

        # If path exists, return it as valid
        if path.exists():
            return ValidatedWindowsPath(path_str, is_valid=True)

        # Try to remap if it's a network path
        original_drive = path_str[:2] if len(path_str) >= 2 else ""
        if original_drive not in cls._network_mappings:
            return ValidatedWindowsPath(path_str, is_valid=False)

        network_folder = cls._network_mappings[original_drive]
        remaining_path = path_str.split("\\", 1)[1] if "\\" in path_str else ""

        # Search through drive letters
        for letter in [f"{chr(i)}:" for i in range(65, 91)]:  # A: through Z:
            try:
                test_path = ValidatedWindowsPath(f"{letter}\\{network_folder}")
                if test_path.exists():
                    new_path = test_path / remaining_path
                    if new_path.exists():
                        print(f"Remapped path to: {new_path}")
                        return ValidatedWindowsPath(new_path, is_valid=True)
            except Exception:
                continue

        print(f"Warning: Could not find valid path for {path_str}")
        print("Please write to et22seol and ask for help")
        return ValidatedWindowsPath(path_str, is_valid=False)
