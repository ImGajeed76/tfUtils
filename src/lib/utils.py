"""File system utilities for safely copying files and directories with progress bar.

This module provides utilities for copying files and
directories with proper error handling, progress tracking,
and support for Windows network paths.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Protocol, Tuple, Union
from urllib.parse import urlparse

import requests
from rich.console import Console
from tqdm import tqdm

PathLike = Union[str, Path]

console = Console()


class FileSystemError(Exception):
    """Base exception for file system operations."""

    pass


class CopyError(FileSystemError):
    """Exception raised when a copy operation fails."""

    pass


class ValidationError(FileSystemError):
    """Exception raised when input validation fails."""

    pass


@dataclass
class CopyStats:
    """Statistics for copy operations."""

    total_files: int = 0
    total_dirs: int = 0
    total_bytes: int = 0
    failed_operations: List[str] = None

    def __post_init__(self):
        self.failed_operations = self.failed_operations or []


class ProgressCallback(Protocol):
    """Protocol for progress callback functions."""

    def __call__(self, current: int, total: int, description: str) -> None:
        """Update progress information."""
        ...


class PathValidator:
    """Utility class for validating file system paths."""

    @staticmethod
    def validate_path_type(path: PathLike, name: str) -> None:
        """Validate that a path is of the correct type."""
        if not isinstance(path, (str, Path)):
            raise ValidationError(f"{name} must be either str or Path object")

    @staticmethod
    def validate_source_exists(path: Path) -> None:
        """Validate that a source path exists."""
        if not path.exists():
            raise FileNotFoundError(f"Source {path} does not exist")

    @staticmethod
    def validate_is_directory(path: Path) -> None:
        """Validate that a path is a directory."""
        if not path.is_dir():
            raise NotADirectoryError(f"Path {path} is not a directory")

    @staticmethod
    def validate_is_file(path: Path) -> None:
        """Validate that a path is a file."""
        if not path.is_file():
            raise IsADirectoryError(f"Path {path} is not a file")


class ProgressTracker:
    """Handles progress tracking for file operations."""

    def __init__(self, console: Console):
        self.console = console

    def create_progress_bar(
        self, total: int, description: str, unit: str = "B", unit_scale: bool = True
    ) -> tqdm:
        """Create a progress bar for tracking operations."""
        return tqdm(total=total, desc=description, unit=unit, unit_scale=unit_scale)

    def update_progress(self, pbar: tqdm, amount: int) -> None:
        """Update the progress bar."""
        pbar.update(amount)


class FileCopier:
    """Handles file copy operations with progress tracking."""

    def __init__(self, console: Console):
        self.console = console
        self.validator = PathValidator()
        self.progress = ProgressTracker(console)

    def copy_file(
        self, source: PathLike, destination: PathLike, buffer_size: int = 8192
    ) -> None:
        """Copy a single file with progress tracking.

        Args:
            source: Source file path
            destination: Destination path (file or directory)
            buffer_size: Size of the buffer for copying

        Raises:
            CopyError: If the copy operation fails
        """
        source_path = Path(source)
        dest_path = Path(destination)

        try:
            # Validate inputs
            self.validator.validate_path_type(source, "source")
            self.validator.validate_path_type(destination, "destination")
            self.validator.validate_source_exists(source_path)
            self.validator.validate_is_file(source_path)

            # Handle destination path
            if dest_path.is_dir():
                dest_path = dest_path / source_path.name

            # Ensure destination directory exists
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy with progress tracking
            file_size = source_path.stat().st_size
            with self.progress.create_progress_bar(
                file_size, f"Copying {source_path.name}"
            ) as pbar:
                with open(source_path, "rb") as fsrc, open(dest_path, "wb") as fdst:
                    while True:
                        buffer = fsrc.read(buffer_size)
                        if not buffer:
                            break
                        fdst.write(buffer)
                        self.progress.update_progress(pbar, len(buffer))

            self.console.print(
                f"[green]Successfully copied {source_path} to {dest_path}"
            )

        except Exception as e:
            raise CopyError(f"Failed to copy {source_path}: {str(e)}") from e


class DirectoryCopier:
    """Handles directory copy operations with progress tracking."""

    def __init__(self, console: Console):
        self.console = console
        self.validator = PathValidator()
        self.progress = ProgressTracker(console)
        self.file_copier = FileCopier(console)

    def copy_directory(
        self, source: PathLike, destination: PathLike, stats: Optional[CopyStats] = None
    ) -> CopyStats:
        """Recursively copy a directory with progress tracking.

        Args:
            source: Source directory path
            destination: Destination directory path
            stats: Optional statistics object for tracking copy operations

        Returns:
            CopyStats object with copy operation statistics

        Raises:
            CopyError: If the copy operation fails
        """
        source_path = Path(source)
        dest_path = Path(destination)
        stats = stats or CopyStats()

        try:
            # Validate inputs
            self.validator.validate_path_type(source, "source")
            self.validator.validate_path_type(destination, "destination")
            self.validator.validate_source_exists(source_path)
            self.validator.validate_is_directory(source_path)

            # Create destination directory
            dest_path.mkdir(parents=True, exist_ok=True)
            stats.total_dirs += 1

            # Get items to copy
            items = list(source_path.glob("*"))

            with self.progress.create_progress_bar(
                len(items), "Copying", unit="item", unit_scale=False
            ) as pbar:
                for item in items:
                    try:
                        if item.is_file():
                            self.file_copier.copy_file(item, dest_path)
                            stats.total_files += 1
                            stats.total_bytes += item.stat().st_size
                        elif item.is_dir():
                            new_dest = dest_path / item.name
                            self.copy_directory(item, new_dest, stats)
                        pbar.update(1)
                    except Exception as e:
                        stats.failed_operations.append(f"{item}: {str(e)}")

            return stats

        except Exception as e:
            raise CopyError(f"Failed to copy directory {source_path}: {str(e)}") from e


class DownloadError(FileSystemError):
    """Exception raised when a download operation fails."""

    pass


class DownloadValidator(PathValidator):
    """Validator for download operations."""

    @staticmethod
    def validate_url(url: str) -> None:
        """Validate that a URL is properly formatted."""
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                raise ValidationError("Invalid URL format") from None
        except Exception as err:
            raise ValidationError(f"Invalid URL: {str(err)}") from err

    @staticmethod
    def validate_response(response: requests.Response) -> None:
        """Validate the response from the server."""
        response.raise_for_status()
        if "content-length" not in response.headers:
            raise ValidationError("Server did not provide content length")


class Downloader:
    """Handles file downloads with progress tracking."""

    def __init__(self, console: Console):
        self.console = console
        self.validator = DownloadValidator()
        self.progress = ProgressTracker(console)

    def download_file(
        self, url: str, destination: PathLike, chunk_size: int = 8192
    ) -> Tuple[Path, int]:
        """
        Download a file with progress tracking.

        Args:
            url: URL to download from
            destination: Destination path (file or directory)
            chunk_size: Size of chunks to download

        Returns:
            Tuple of (Path to downloaded file, total bytes downloaded)

        Raises:
            DownloadError: If the download operation fails
        """
        try:
            # Validate URL
            self.validator.validate_url(url)

            # Validate and prepare destination
            dest_path = Path(destination)
            self.validator.validate_path_type(destination, "destination")

            # If destination is a directory, use filename from URL
            if dest_path.is_dir():
                filename = url.split("/")[-1]
                dest_path = dest_path / filename

            # Ensure destination directory exists
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Start download with progress tracking
            with requests.get(url, stream=True) as response:
                self.validator.validate_response(response)

                total_size = int(response.headers["content-length"])
                with self.progress.create_progress_bar(
                    total_size,
                    f"Downloading {dest_path.name}",
                    unit="B",
                    unit_scale=True,
                ) as pbar:
                    with open(dest_path, "wb") as f:
                        for chunk in response.iter_content(chunk_size=chunk_size):
                            if chunk:
                                f.write(chunk)
                                self.progress.update_progress(pbar, len(chunk))

            self.console.print(f"[green]Successfully downloaded to {dest_path}")
            return dest_path, total_size

        except requests.RequestException as e:
            raise DownloadError(f"Download failed: {str(e)}") from e
        except Exception as e:
            raise DownloadError(f"Download operation failed: {str(e)}") from e


class FileSystemOperations:
    """High-level interface for file system operations."""

    def __init__(self):
        self.console = Console()
        self.file_copier = FileCopier(self.console)
        self.dir_copier = DirectoryCopier(self.console)
        self.downloader = Downloader(self.console)

    def safe_copy_file(self, source: PathLike, destination: PathLike) -> None:
        """Safely copy a file with error handling."""
        try:
            self.file_copier.copy_file(source, destination)
        except Exception as e:
            self.console.print(f"[bold red]Error: {str(e)}")

    def safe_copy_directory(self, source: PathLike, destination: PathLike) -> None:
        """Safely copy a directory with error handling."""
        try:
            stats = self.dir_copier.copy_directory(source, destination)
            self.print_copy_stats(stats)
        except Exception as e:
            self.console.print(f"[bold red]Error: {str(e)}")

    def get_files_in_directory(self, directory: PathLike) -> List[Path]:
        """Get all files in a directory and its subdirectories."""
        try:
            dir_path = Path(directory)
            PathValidator.validate_path_type(directory, "directory")
            PathValidator.validate_source_exists(dir_path)
            PathValidator.validate_is_directory(dir_path)
            return list(dir_path.rglob("*"))
        except Exception as e:
            self.console.print(f"[bold red]Error listing files: {str(e)}")
            return []

    def print_copy_stats(self, stats: CopyStats) -> None:
        """Print copy operation statistics."""
        self.console.print("\n[bold green]Copy Operation Summary:")
        self.console.print(f"Total directories: {stats.total_dirs}")
        self.console.print(f"Total files: {stats.total_files}")
        self.console.print(
            f"Total bytes copied: {stats.total_bytes:,} "
            f"({stats.total_bytes / 1024 / 1024:.2f} MB)"
        )

        if stats.failed_operations:
            self.console.print("\n[bold red]Failed Operations:")
            for failure in stats.failed_operations:
                self.console.print(f"- {failure}")

    def safe_download(
        self, url: str, destination: PathLike
    ) -> Tuple[Optional[Path], Optional[str]]:
        """
        Safely download a file with error handling.

        Args:
            url: URL to download from
            destination: Destination path (file or directory)

        Returns:
            Tuple of (Path to downloaded file or None, error message or None)
        """
        try:
            file_path, total_bytes = self.downloader.download_file(url, destination)
            self.console.print(
                f"\n[bold green]Download Summary:"
                f"\nFile: {file_path.name}"
                f"\nSize: {total_bytes:,} bytes ({total_bytes / 1024 / 1024:.2f} MB)"
            )
            return file_path, None
        except Exception as e:
            error_msg = f"Download failed: {str(e)}"
            self.console.print(f"[bold red]Error: {error_msg}")
            return None, error_msg


# Create a global instance for convenient access
fs_ops = FileSystemOperations()


# Provide convenience functions at module level
def safe_copy_file(source: PathLike, destination: PathLike) -> None:
    """Convenience function for safely copying a file."""
    fs_ops.safe_copy_file(source, destination)


def safe_copy_directory(source: PathLike, destination: PathLike) -> None:
    """Convenience function for safely copying a directory."""
    fs_ops.safe_copy_directory(source, destination)


def get_copied_files(directory: PathLike) -> List[Path]:
    """Convenience function for getting files in a directory."""
    return fs_ops.get_files_in_directory(directory)


def safe_download(
    url: str, destination: PathLike
) -> Tuple[Optional[Path], Optional[str]]:
    """Convenience function for safely downloading a file."""
    return fs_ops.safe_download(url, destination)
