"""File system utilities for safely copying files and directories with progress bar.

This module provides utilities for copying files and
directories with proper error handling, progress tracking,
and support for Windows network paths.
"""

import asyncio
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
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


class DownloadError(FileSystemError):
    """Exception raised when a download operation fails."""

    pass


class PathValidator:
    """Utility class for validating file system paths."""

    @staticmethod
    def validate_path_type(path: PathLike, name: str) -> None:
        if not isinstance(path, (str, Path)):
            raise ValidationError(f"{name} must be either str or Path object")

    @staticmethod
    def validate_source_exists(path: Path) -> None:
        if not path.exists():
            raise FileNotFoundError(f"Source {path} does not exist")

    @staticmethod
    def validate_is_file(path: Path) -> None:
        if not path.is_file():
            raise IsADirectoryError(f"Path {path} is not a file")

    @staticmethod
    def validate_is_directory(path: Path) -> None:
        if not path.is_dir():
            raise NotADirectoryError(f"Path {path} is not a directory")


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


class ProgressTracker:
    """Handles progress tracking for file operations."""

    def __init__(self, container: Container):
        self.container = container

    async def create_progress_bar(self, total: int) -> ProgressBar:
        progress_bar = ProgressBar(total=total)
        await self.container.mount(progress_bar)
        return progress_bar

    @staticmethod
    async def advance_progress(pbar: ProgressBar, amount: int) -> None:
        if pbar.total is not None:
            pbar.advance(amount)
            pbar.refresh()


class FileCopier:
    """Handles file copy operations with optimized performance."""

    def __init__(self, container: Container):
        self.container = container
        self.validator = PathValidator()
        self.progress = ProgressTracker(container)
        self._copy_semaphore = asyncio.Semaphore(10)

    async def copy_file(
        self,
        source: PathLike,
        destination: PathLike,
    ) -> Tuple[int, Optional[str]]:
        """Copy a single file with optimized progress tracking.

        Uses a hybrid approach combining shutil for speed with async monitoring
        for progress tracking.

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

                # Set up progress tracking
                file_size = source_path.stat().st_size
                pbar = await self.progress.create_progress_bar(file_size)

                async def monitor_progress():
                    """Monitor copy progress asynchronously"""
                    dst_size = 0
                    while dst_size < file_size:
                        try:
                            current_size = dest_path.stat().st_size
                            delta = current_size - dst_size
                            if delta > 0:
                                await self.progress.advance_progress(pbar, delta)
                            dst_size = current_size
                        except FileNotFoundError:
                            await asyncio.sleep(0.1)
                        await asyncio.sleep(0.1)

                async def copy_file():
                    """Perform the actual file copy operation"""
                    await asyncio.to_thread(shutil.copy2, source_path, dest_path)

                # Create and run tasks
                copy_task = asyncio.create_task(copy_file())
                monitor_task = asyncio.create_task(monitor_progress())

                try:
                    await copy_task
                finally:
                    monitor_task.cancel()
                    try:
                        await monitor_task
                    except asyncio.CancelledError:
                        pass

                # Final progress update
                final_size = dest_path.stat().st_size
                if final_size != file_size:
                    error_msg = (
                        f"File size mismatch! Expected {file_size}, got {final_size}"
                    )
                    await self.container.mount(Label(f"[red]{error_msg}[/red]"))
                    return 0, error_msg

                await self.progress.advance_progress(pbar, file_size)

                await self.container.mount(
                    Label(f"[green]Successfully copied {source_path.name}[/green]")
                )
                return file_size, None

        except Exception as e:
            error_msg = f"Failed to copy {source_path}: \n{str(e)}"
            await self.container.mount(Label(f"[red]{error_msg}[/red]"))
            return 0, error_msg


class DirectoryCopier:
    """
    Handles directory copy operations with progress tracking using shutil.copytree.
    """

    def __init__(self, container: Container):
        self.container = container
        self.validator = PathValidator()
        self.progress = ProgressTracker(container)
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

    async def copy_directory(
        self, source: PathLike, destination: PathLike
    ) -> Tuple[int, Optional[str]]:
        """Copy a directory using shutil.copytree with progress tracking.

        Args:
            source: Source directory path
            destination: Destination directory path
            stats: Optional CopyStats object for tracking progress

        Returns:
            CopyStats object with copy operation statistics
        """
        source_path = Path(source)
        dest_path = Path(destination)

        try:
            # Validate inputs
            self.validator.validate_path_type(source, "source")
            self.validator.validate_path_type(destination, "destination")
            self.validator.validate_source_exists(source_path)
            self.validator.validate_is_directory(source_path)

            # Set up progress tracking
            folder_size = await self.get_dir_size(source_path)
            pbar = await self.progress.create_progress_bar(folder_size)

            # Custom copy function that updates progress
            async def monitor_progress():
                """Monitor copy progress asynchronously"""
                copied_size = 0
                while copied_size < folder_size:
                    try:
                        current_size = await self.get_dir_size(dest_path)
                        delta = current_size - copied_size
                        if delta > 0:
                            await self.progress.advance_progress(pbar, delta)
                        copied_size = current_size
                    except FileNotFoundError:
                        await asyncio.sleep(0.1)
                    await asyncio.sleep(0.1)

            # Use shutil.copytree with custom copy function
            async def copy_directory():
                """Perform the actual directory copy operation"""
                await asyncio.to_thread(
                    shutil.copytree,
                    source_path,
                    dest_path,
                    symlinks=True,
                    dirs_exist_ok=True,
                )

            copy_task = asyncio.create_task(copy_directory())
            monitor_task = asyncio.create_task(monitor_progress())

            try:
                await copy_task
            finally:
                monitor_task.cancel()
                try:
                    await monitor_task
                except asyncio.CancelledError:
                    pass

            # Final progress update
            final_size = await self.get_dir_size(dest_path)
            if final_size != folder_size:
                error_msg = (
                    f"Directory size mismatch! Expected {folder_size}, got {final_size}"
                )
                await self.container.mount(Label(f"[red]{error_msg}[/red]"))
                return 0, error_msg

            await self.progress.advance_progress(pbar, folder_size)

            await self.container.mount(
                Label(f"[green]Successfully copied directory {source_path}[/green]")
            )
            return folder_size, None

        except Exception as e:
            error_msg = f"Failed to copy directory {source_path}: \n{str(e)}"
            await self.container.mount(Label(f"[red]{error_msg}[/red]"))
            return 0, error_msg


class Downloader:
    """Handles file downloads with optimized performance and robust error handling."""

    def __init__(self, container: Container):
        self.container = container
        self.validator = DownloadValidator()
        self.progress = ProgressTracker(container)
        self._download_semaphore = asyncio.Semaphore(10)
        self._session: Optional[aiohttp.ClientSession] = None
        self._connection_label: Optional[Label] = None
        self.retry_config = {
            "max_retries": 3,
            "initial_delay": 0.5,
            "max_delay": 5,
            "backoff_factor": 1.5,
        }
        self.conn_kwargs = {
            "limit": 30,
            "ttl_dns_cache": 300,
            "force_close": False,
        }

    async def __aenter__(self):
        """Context manager entry - creates optimized session with connection pooling."""
        tcp_connector = aiohttp.TCPConnector(**self.conn_kwargs)
        self._session = aiohttp.ClientSession(
            connector=tcp_connector,
            timeout=aiohttp.ClientTimeout(total=None, connect=10),
            headers={"Connection": "keep-alive"},
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures proper cleanup of resources."""
        if self._session:
            await self._session.close()
            self._session = None
        if self._connection_label:
            await self._connection_label.remove()
            self._connection_label = None

    async def _show_connection_status(self, message: str) -> None:
        """Show or update connection status message."""
        if self._connection_label:
            await self._connection_label.remove()
        self._connection_label = Label(f"[yellow]{message}[/yellow]")
        await self.container.mount(self._connection_label)

    async def _clear_connection_status(self) -> None:
        """Clear the connection status message."""
        if self._connection_label:
            await self._connection_label.remove()
            self._connection_label = None

    async def _check_internet_connection(self) -> bool:
        """Check if there's an active internet connection."""
        try:
            async with self._get_session().get(
                "https://8.8.8.8", timeout=1
            ) as response:
                return response.status == 200
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return False

    async def _wait_for_connection(self) -> None:
        """Wait for internet connection to be restored with exponential backoff."""
        await self._show_connection_status(
            "No internet connection. Waiting for connection to be restored..."
        )
        retry_count = 0
        while not await self._check_internet_connection():
            delay = min(
                self.retry_config["initial_delay"]
                * (self.retry_config["backoff_factor"] ** retry_count),
                self.retry_config["max_delay"],
            )
            await asyncio.sleep(delay)
            retry_count += 1
        await self._clear_connection_status()

    def _get_session(self) -> aiohttp.ClientSession:
        """Get the current session or create a new one."""
        if self._session is None:
            tcp_connector = aiohttp.TCPConnector(**self.conn_kwargs)
            self._session = aiohttp.ClientSession(
                connector=tcp_connector,
                timeout=aiohttp.ClientTimeout(total=None, connect=10),
                headers={"Connection": "keep-alive"},
            )
        return self._session

    async def _verify_partial_download(self, path: Path, expected_size: int) -> bool:
        """Verify if a partial download is valid and matches expected size."""
        if not path.exists():
            return False
        try:
            current_size = path.stat().st_size
            if current_size > expected_size:
                path.unlink()  # Remove corrupted file
                return False
            return True
        except OSError:
            return False

    async def _handle_rate_limit(self, response: aiohttp.ClientResponse) -> None:
        """Handle rate limiting by waiting for the specified time."""
        if response.status == 429:  # Too Many Requests
            retry_after = int(response.headers.get("Retry-After", "5"))
            await self.container.mount(
                Label(
                    f"[yellow]Rate limited. Waiting {retry_after} seconds...[/yellow]"
                )
            )
            await asyncio.sleep(retry_after)

    async def _download_with_retry(
        self, url: str, dest_path: Path, chunk_size: int
    ) -> Tuple[Path, int]:
        """Optimized download with retry logic and resumption capability."""
        retry_count = 0
        total_size = 0
        current_size = 0
        pbar = None

        chunk_size = chunk_size * 4  # Increased chunk size

        while retry_count < self.retry_config["max_retries"]:
            try:
                if not await self._check_internet_connection():
                    await self._wait_for_connection()

                headers = {
                    "Accept-Encoding": "gzip, deflate",  # Enable compression
                    "Connection": "keep-alive",
                }

                if dest_path.exists():
                    current_size = dest_path.stat().st_size
                    headers["Range"] = f"bytes={current_size}-"

                async with self._get_session().get(
                    url, headers=headers, timeout=300
                ) as response:
                    await self._handle_rate_limit(response)
                    self.validator.validate_response(response)

                    if response.status == 206:  # Partial Content
                        total_size = current_size + int(
                            response.headers["Content-Length"]
                        )
                    else:
                        total_size = int(response.headers["Content-Length"])
                        current_size = 0

                    if not pbar:
                        pbar = await self.progress.create_progress_bar(total_size)
                        if current_size:
                            await self.progress.advance_progress(pbar, current_size)

                    # Use buffered writing for better performance
                    mode = "ab" if current_size > 0 else "wb"
                    async with aiofiles.open(dest_path, mode, buffering=8192 * 4) as f:
                        async for chunk in response.content.iter_chunked(chunk_size):
                            if not await self._check_internet_connection():
                                await self._wait_for_connection()
                                continue

                            if chunk:
                                await f.write(chunk)
                                await self.progress.advance_progress(pbar, len(chunk))

                if await self._verify_partial_download(dest_path, total_size):
                    return dest_path, total_size

                raise DownloadError("Download verification failed")

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if not await self._check_internet_connection():
                    await self._wait_for_connection()
                    continue

                retry_count += 1
                if retry_count >= self.retry_config["max_retries"]:
                    raise DownloadError(
                        f"Download failed after {retry_count} retries: {str(e)}"
                    ) from None

                delay = min(
                    self.retry_config["initial_delay"]
                    * (self.retry_config["backoff_factor"] ** (retry_count - 1)),
                    self.retry_config["max_delay"],
                )
                await self.container.mount(
                    Label(
                        f"[yellow]Retry {retry_count} after {delay}s: {str(e)}[/yellow]"
                    )
                )
                await asyncio.sleep(delay)

    async def download_file(
        self,
        url: str,
        destination: PathLike,
        chunk_size: int = 1024 * 1024 * 4,  # Increased default chunk size
    ) -> Tuple[Path, int]:
        """
        Download a single file with optimized performance and robust error handling.

        Args:
            url: URL to download from
            destination: Destination path (file or directory)
            chunk_size: Size of chunks to download (default: 4MB)

        Returns:
            Tuple of (Path to downloaded file, total bytes downloaded)

        Raises:
            DownloadError: If the download operation fails after all retries
        """
        try:
            # Validate URL and prepare destination
            self.validator.validate_url(url)
            dest_path = Path(destination)

            if dest_path.is_dir():
                filename = url.split("/")[-1]
                dest_path = dest_path / filename

            # Ensure destination directory exists
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Perform download with retry logic
            file_path, total_size = await self._download_with_retry(
                url, dest_path, chunk_size
            )

            await self.container.mount(
                Label(
                    f"[green]"
                    f"Successfully downloaded to {file_path} "
                    f"({total_size / 1024 / 1024:.2f} MB)"
                    f"[/green]"
                )
            )

            return file_path, total_size

        except Exception as e:
            if dest_path.exists() and dest_path.stat().st_size == 0:
                dest_path.unlink()  # Clean up empty file
            raise DownloadError(f"Download operation failed: {str(e)}") from e

    async def download_files(
        self, urls: List[str], destination: PathLike, chunk_size: int = 1024 * 1024 * 4
    ) -> Dict[str, Tuple[Optional[Path], Optional[str]]]:
        """
        Download multiple files in parallel with optimized performance.

        Args:
            urls: List of URLs to download from
            destination: Destination directory
            chunk_size: Size of chunks to download (default: 4MB)

        Returns:
            Dict mapping URLs to
            (Path to downloaded file or None, error message or None)
        """
        dest_path = Path(destination)
        if not dest_path.is_dir():
            raise ValidationError("Destination must be a directory")

        async def download_single(url: str) -> Tuple[Optional[Path], Optional[str]]:
            try:
                async with self._download_semaphore:
                    downloaded_file, _ = await self.download_file(
                        url, dest_path, chunk_size
                    )
                    return downloaded_file, None
            except Exception as e:
                return None, str(e)

        # Use connection pooling for multiple downloads
        async with self:
            # Create tasks for parallel downloads
            tasks = [download_single(url) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            successful = sum(
                1
                for result in results
                if isinstance(result, tuple) and result[0] is not None
            )
            await self.container.mount(
                Label(
                    f"[bold]Download Summary:[/bold]\n"
                    f"Total: {len(urls)}\n"
                    f"Successful: {successful}\n"
                    f"Failed: {len(urls) - successful}"
                )
            )

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
        self, source: PathLike, destination: PathLike
    ) -> None:
        """Safely copy a directory with error handling."""
        try:
            await self.dir_copier.copy_directory(source, destination)
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

    async def safe_downloads(
        self, urls: List[str], destination_folder: PathLike
    ) -> Dict[str, Tuple[Optional[Path], Optional[str]]]:
        """Safely download multiple files with error handling."""
        try:
            downloads = await self.downloader.download_files(urls, destination_folder)
            await self.container.mount(
                Label(
                    f"[bold green]"
                    f"Downloaded {len(downloads)} files successfully."
                    f"[/bold green]"
                )
            )
            return downloads
        except Exception as e:
            error_msg = f"Failed to download files: {str(e)}"
            await self.container.mount(
                Label(f"[bold red]Error: {error_msg}[/bold red]")
            )
            return {url: (None, error_msg) for url in urls}


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
) -> None:
    """Convenience function for safely copying a directory."""
    fs_ops = FileSystemOperations(container)
    await fs_ops.safe_copy_directory(source, destination)


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
    return await fs_ops.safe_downloads(urls, destination)
