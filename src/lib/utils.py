"""File system utilities for safely copying files and directories with progress bar.

This module provides utilities for copying files and
directories with proper error handling, progress tracking,
and support for Windows network paths.
"""

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Protocol, Tuple, Union
from urllib.parse import urlparse

import aiofiles
import aiohttp
from textual.containers import Container
from textual.widgets import Label, ProgressBar

PathLike = Union[str, Path]


class Console:
    @staticmethod
    async def print(container: Container, message: str) -> None:
        """Print a message to the container."""
        await container.mount(Label(message))


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

    def __init__(self, container: Container):
        self.container = container

    async def create_progress_bar(self, total: int) -> ProgressBar:
        """Create a progress bar for tracking operations."""
        progress_bar = ProgressBar(total=total)
        await self.container.mount(progress_bar)
        return progress_bar

    @staticmethod
    async def advance_progress(pbar: ProgressBar, amount: int) -> None:
        """Update the progress bar asynchronously."""
        if pbar.total is not None:  # Check if we have a total to avoid division by zero
            pbar.advance(amount)
            pbar.refresh()


class FileCopier:
    """Handles file copy operations with optimized performance."""

    def __init__(self, container: Container):
        self.container = container
        self.validator = PathValidator()
        self.progress = ProgressTracker(container)
        self._copy_semaphore = asyncio.Semaphore(10)
        self._progress_update_interval = 0.1  # Update progress every 100ms
        self._last_progress_update = 0

    async def copy_file(
        self,
        source: PathLike,
        destination: PathLike,
        buffer_size: int = 1024 * 1024 * 100,
    ) -> Tuple[int, Optional[str]]:
        """Copy a single file with optimized progress tracking.

        Improvements:
        - Increased buffer size to 1MB for better throughput
        - Throttled progress updates to reduce UI overhead
        - Batched progress updates
        - Reduced container mounting frequency

        Returns:
            Tuple[int, Optional[str]]: (bytes copied, error message if failed)
        """
        source_path = Path(source)
        dest_path = Path(destination)

        try:
            async with self._copy_semaphore:
                # Validate inputs
                self.validator.validate_path_type(source, "source")
                self.validator.validate_path_type(destination, "destination")
                self.validator.validate_source_exists(source_path)
                self.validator.validate_is_file(source_path)

                if dest_path.is_dir():
                    dest_path = dest_path / source_path.name

                # Ensure destination directory exists
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                # Copy with optimized progress tracking
                file_size = source_path.stat().st_size
                pbar = await self.progress.create_progress_bar(file_size)

                accumulated_progress = 0
                current_time = asyncio.get_event_loop().time()

                async with aiofiles.open(source_path, "rb") as fsrc:
                    async with aiofiles.open(dest_path, "wb") as fdst:
                        while True:
                            chunk = await fsrc.read(buffer_size)
                            if not chunk:
                                break

                            await fdst.write(chunk)
                            accumulated_progress += len(chunk)

                            # Update progress bar less frequently
                            new_time = asyncio.get_event_loop().time()
                            if (
                                new_time - current_time
                            ) >= self._progress_update_interval:
                                await self.progress.advance_progress(
                                    pbar, accumulated_progress
                                )
                                accumulated_progress = 0
                                current_time = new_time

                # Final progress update
                if accumulated_progress > 0:
                    await self.progress.advance_progress(pbar, accumulated_progress)

                # Only mount completion message for larger files
                if file_size > 10 * 1024 * 1024:  # 10MB
                    await self.container.mount(
                        Label(f"[green]Successfully copied {source_path.name}[/green]")
                    )

                return file_size, None

        except Exception as e:
            error_msg = f"Failed to copy {source_path}: {str(e)}"
            await self.container.mount(Label(f"[red]{error_msg}[/red]"))
            return 0, error_msg


class DirectoryCopier:
    """Handles parallel directory copy operations with progress tracking."""

    def __init__(self, container: Container):
        self.container = container
        self.validator = PathValidator()
        self.progress = ProgressTracker(container)
        self.file_copier = None
        self.vertical_container = None
        self._scan_semaphore = asyncio.Semaphore(10)  # Limit concurrent directory scans

    async def get_dir_size(self, path: Path) -> int:
        """Calculate total size of all files in directory using parallel scanning."""
        total_size = 0
        async with self._scan_semaphore:
            for item in path.rglob("*"):
                if item.is_file():
                    try:
                        total_size += item.stat().st_size
                    except OSError:
                        continue
        return total_size

    async def scan_directory(self, path: Path) -> Tuple[List[Path], List[Path]]:
        """Scan directory and return lists of files and subdirectories."""
        files = []
        dirs = []
        try:
            async with self._scan_semaphore:
                for item in path.rglob("*"):
                    try:
                        if item.is_file():
                            files.append(item)
                        elif item.is_dir():
                            dirs.append(item)
                    except OSError:
                        continue
        except Exception as e:
            await self.container.mount(
                Label(f"[red]Error scanning directory {path}: {str(e)}[/red]")
            )
        return files, dirs

    @staticmethod
    async def count_items(path: Path) -> Tuple[int, int]:
        """Count total files and directories."""
        files = 0
        dirs = 0
        for item in path.rglob("*"):
            try:
                if item.is_file():
                    files += 1
                elif item.is_dir():
                    dirs += 1
            except OSError:
                continue  # Skip items we can't access
        return files, dirs

    async def setup_progress_tracking(
        self, source_path: Path
    ) -> Tuple[ProgressBar, Container]:
        """Set up progress tracking UI elements."""
        total_size = await self.get_dir_size(source_path)
        total_files, total_dirs = await self.count_items(source_path)

        await self.container.mount(
            Label(
                f"[blue]Found {total_files} files and {total_dirs} directories "
                f"({total_size / 1024 / 1024:.2f} MB total)[/blue]"
            )
        )

        progress_bar = await self.progress.create_progress_bar(total_size)

        vertical_container = Container()
        vertical_container.styles.max_height = 20
        vertical_container.styles.overflow_y = "scroll"
        await self.container.mount(vertical_container)

        return progress_bar, vertical_container

    async def copy_directory(
        self,
        source: PathLike,
        destination: PathLike,
        stats: Optional[CopyStats] = None,
        max_concurrent_copies: int = 5,
    ) -> CopyStats:
        """Recursively copy a directory with parallel file operations."""
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

            # Initialize progress tracking
            if self.file_copier is None:
                pbar, self.vertical_container = await self.setup_progress_tracking(
                    source_path
                )
                self.file_copier = FileCopier(self.vertical_container)

            # Scan directory structure
            files, dirs = await self.scan_directory(source_path)

            # Create all required directories first
            for dir_path in dirs:
                rel_path = dir_path.relative_to(source_path)
                new_dir = dest_path / rel_path
                new_dir.mkdir(parents=True, exist_ok=True)
                stats.total_dirs += 1

            async def copy_wrapper(fp: Path, df: Path):
                return_value = await self.file_copier.copy_file(fp, df)
                file_size = fp.stat().st_size
                await self.progress.advance_progress(pbar, file_size)
                if self.vertical_container:
                    self.vertical_container.scroll_end()
                return return_value

            # Copy files in parallel
            copy_tasks = []
            for file_path in files:
                rel_path = file_path.relative_to(source_path)
                dest_file = dest_path / rel_path
                copy_tasks.append(copy_wrapper(file_path, dest_file))

            # Use asyncio.gather to run copies in parallel with concurrency limit
            results = []
            for i in range(0, len(copy_tasks), max_concurrent_copies):
                batch = copy_tasks[i : i + max_concurrent_copies]
                batch_results = await asyncio.gather(*batch, return_exceptions=True)
                results.extend(batch_results)

            # Process results
            for size, error in results:
                if error is None:
                    stats.total_files += 1
                    stats.total_bytes += size
                else:
                    stats.failed_operations.append(error)

            return stats

        except Exception as e:
            error_msg = f"Failed to copy directory {source_path}: {str(e)}"
            stats.failed_operations.append(error_msg)
            await self.container.mount(Label(f"[red]{error_msg}[/red]"))
            return stats


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
    def validate_response(response: aiohttp.ClientResponse) -> None:
        """Validate the response from the server."""
        if response.status >= 400:
            raise ValidationError(f"Server returned error status: {response.status}")
        if "content-length" not in response.headers:
            raise ValidationError("Server did not provide content length")


class Downloader:
    """Handles file downloads with progress tracking."""

    def __init__(self, container: Container):
        self.container = container
        self.validator = DownloadValidator()
        self.progress = ProgressTracker(container)
        self._download_semaphore = asyncio.Semaphore(3)  # Limit concurrent downloads

    async def download_file(
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
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    self.validator.validate_response(response)

                    total_size = int(response.headers["content-length"])
                    pbar = await self.progress.create_progress_bar(total_size)

                    with open(dest_path, "wb") as f:
                        downloaded = 0
                        async for chunk in response.content.iter_chunked(chunk_size):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                await self.progress.advance_progress(pbar, len(chunk))

            await self.container.mount(
                Label(f"[green]Successfully downloaded to {dest_path} [/green]")
            )

            return dest_path, total_size

        except aiohttp.ClientError as e:
            raise DownloadError(f"Download failed: {str(e)}") from e
        except Exception as e:
            raise DownloadError(f"Download operation failed: {str(e)}") from e

    async def download_files(
        self, urls: List[str], destination: PathLike, chunk_size: int = 8192
    ) -> Dict[str, Tuple[Optional[Path], Optional[str]]]:
        """
        Download multiple files in parallel with progress tracking.

        Args:
            urls: List of URLs to download from
            destination: Destination directory
            chunk_size: Size of chunks to download

        Returns:
            Dict mapping URLs to
            (Path to downloaded file or None, error message or None)
        """
        dest_path = Path(destination)
        if not dest_path.is_dir():
            raise ValidationError("Destination must be a directory")

        async def download_single(url: str) -> tuple[Path, int] | tuple[None, str]:
            try:
                async with self._download_semaphore:
                    return await self.download_file(url, dest_path, chunk_size)
            except Exception as e:
                return None, str(e)

        tasks = [download_single(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return dict(zip(urls, results))


class FileSystemOperations:
    """High-level interface for file system operations."""

    def __init__(self, container: Container):
        self.container = container
        self.file_copier = FileCopier(self.container)
        self.dir_copier = DirectoryCopier(self.container)
        self.downloader = Downloader(self.container)

    async def safe_copy_file(self, source: PathLike, destination: PathLike) -> None:
        """Safely copy a file with error handling."""
        try:
            await self.file_copier.copy_file(source, destination)
        except Exception as e:
            await self.container.mount(Label(f"[bold red]Error: {str(e)}[/bold red]"))

    async def safe_copy_directory(
        self, source: PathLike, destination: PathLike, max_concurrent_copies=5
    ) -> None:
        """Safely copy a directory with error handling."""
        try:
            stats = await self.dir_copier.copy_directory(
                source, destination, max_concurrent_copies=max_concurrent_copies
            )
            await self.print_copy_stats(stats)
        except Exception as e:
            await self.container.mount(Label(f"[bold red]Error: {str(e)}[/bold red]"))

    async def get_files_in_directory(self, directory: PathLike) -> List[Path]:
        """Get all files in a directory and its subdirectories."""
        try:
            dir_path = Path(directory)
            PathValidator.validate_path_type(directory, "directory")
            PathValidator.validate_source_exists(dir_path)
            PathValidator.validate_is_directory(dir_path)
            return list(dir_path.rglob("*"))
        except Exception as e:
            await self.container.mount(
                Label(f"[bold red]Error listing files: {str(e)}[/bold red]")
            )
            return []

    async def print_copy_stats(self, stats: CopyStats) -> None:
        """Print copy operation statistics."""
        await self.container.mount(
            Label("[bold green]Copy Operation Summary:[/bold green]")
        )
        await self.container.mount(Label(f"Total directories: {stats.total_dirs}"))
        await self.container.mount(Label(f"Total files: {stats.total_files}"))
        await self.container.mount(
            Label(
                f"Total bytes copied: {stats.total_bytes:,} "
                f"({stats.total_bytes / 1024 / 1024:.2f} MB)"
            )
        )

        if stats.failed_operations:
            await self.container.mount(Label("[bold red]Failed Operations:[/bold red]"))
            for failure in stats.failed_operations:
                await self.container.mount(Label(f"- {failure}"))

    async def safe_download(
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
            file_path, total_bytes = await self.downloader.download_file(
                url, destination
            )

            await self.container.mount(
                Label(
                    f"[bold green]Download Summary:[/bold green]"
                    f"\nFile: {file_path.name}"
                    f"\nSize: {total_bytes:,} "
                    f"bytes ({total_bytes / 1024 / 1024:.2f} MB)"
                )
            )

            return file_path, None
        except Exception as e:
            error_msg = f"Download failed: {str(e)}"
            await self.container.mount(
                Label(f"[bold red]Error: {error_msg}[/bold red]")
            )
            return None, error_msg


# Provide convenience functions at module level
async def safe_copy_file(
    container: Container, source: PathLike, destination: PathLike
) -> None:
    """Convenience function for safely copying a file."""
    fs_ops = FileSystemOperations(container)
    await fs_ops.safe_copy_file(source, destination)


async def safe_copy_directory(
    container: Container,
    source: PathLike,
    destination: PathLike,
    max_concurrent_copies=5,
) -> None:
    """Convenience function for safely copying a directory."""
    fs_ops = FileSystemOperations(container)
    await fs_ops.safe_copy_directory(
        source, destination, max_concurrent_copies=max_concurrent_copies
    )


async def get_copied_files(container: Container, directory: PathLike) -> List[Path]:
    """Convenience function for getting files in a directory."""
    fs_ops = FileSystemOperations(container)
    return await fs_ops.get_files_in_directory(directory)


async def safe_download(
    container: Container, url: str, destination: PathLike
) -> Tuple[Optional[Path], Optional[str]]:
    """Convenience function for safely downloading a file."""
    fs_ops = FileSystemOperations(container)
    return await fs_ops.safe_download(url, destination)


async def safe_download_files(
    container: Container, urls: List[str], destination: PathLike
) -> Dict[str, Tuple[Optional[Path], Optional[str]]]:
    """Convenience function for safely downloading multiple files."""
    fs_ops = FileSystemOperations(container)
    return await fs_ops.downloader.download_files(urls, destination)
