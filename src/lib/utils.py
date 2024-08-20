import shutil
from pathlib import Path
from typing import Union, List

from rich.console import Console

console = Console()


def copy_directory_recursively(source_dir: Union[str, Path], destination_dir: Union[str, Path]) -> None:
    """
    Recursively copy a directory and its contents, designed to work with Windows network paths.

    :param source_dir: Path to the source directory
    :param destination_dir: Path to the destination directory
    :raises TypeError: If inputs are not str or Path
    :raises FileNotFoundError: If source_dir doesn't exist
    :raises NotADirectoryError: If source_dir is not a directory
    """
    # Convert to Path objects and validate inputs
    source_path = Path(source_dir)
    destination_path = Path(destination_dir)

    if not isinstance(source_dir, (str, Path)) or not isinstance(destination_dir, (str, Path)):
        raise TypeError("Both source_dir and destination_dir must be either str or Path objects")

    if not source_path.exists():
        raise FileNotFoundError(f"Source directory {source_path} does not exist")

    if not source_path.is_dir():
        raise NotADirectoryError(f"Source {source_path} is not a directory")

    # Create the destination directory if it doesn't exist
    destination_path.mkdir(parents=True, exist_ok=True)

    for item in source_path.glob('*'):
        if item.is_file():
            shutil.copy2(str(item), str(destination_path / item.name))
        elif item.is_dir():
            new_dest = destination_path / item.name
            copy_directory_recursively(item, new_dest)


def safe_copy_directory(source_dir: Union[str, Path], destination_dir: Union[str, Path]) -> None:
    """
    A wrapper function that safely calls copy_directory_recursively with error handling.

    :param source_dir: Path to the source directory
    :param destination_dir: Path to the destination directory
    """
    try:
        copy_directory_recursively(source_dir, destination_dir)
    except PermissionError:
        print(
            f"Permission denied. Make sure you have the necessary rights to access {source_dir} and write to {destination_dir}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except NotADirectoryError as e:
        print(f"Error: {e}")
    except TypeError as e:
        print(f"Type error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def get_copied_files(directory: Union[str, Path]) -> List[Path]:
    """
    Get a list of all files in the given directory and its subdirectories.

    :param directory: Path to the directory
    :return: List of Path objects representing files
    """
    dir_path = Path(directory)
    return [file for file in dir_path.rglob('*') if file.is_file()]


def safe_copy_file(source_file: Union[str, Path], destination: Union[str, Path]) -> None:
    """
    Safely copy a file from source to destination with error handling.

    :param source_file: Path to the source file
    :param destination: Path to either the destination directory or the full destination file path
    """
    try:
        source_path = Path(source_file)
        destination_path = Path(destination)

        if not isinstance(source_file, (str, Path)) or not isinstance(destination, (str, Path)):
            raise TypeError("Both source_file and destination must be either str or Path objects")

        if not source_path.exists():
            raise FileNotFoundError(f"Source file {source_path} does not exist")

        if not source_path.is_file():
            raise IsADirectoryError(f"Source {source_path} is not a file")

        # If destination is a directory, use the original filename
        if destination_path.is_dir():
            destination_path = destination_path / source_path.name

        # Create the destination directory if it doesn't exist
        destination_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(str(source_path), str(destination_path))
        print(f"File copied successfully from {source_path} to {destination_path}")

    except PermissionError:
        print(f"Permission denied. Make sure you have the necessary rights to access {source_file} and write to {destination}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except IsADirectoryError as e:
        print(f"Error: {e}")
    except TypeError as e:
        print(f"Type error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")