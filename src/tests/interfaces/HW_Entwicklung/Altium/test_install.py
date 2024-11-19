import subprocess
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from textual.containers import Container

from src.interfaces.HW_Entwicklung.Altium.install import (
    get_installer_path,
    install_altium,
)


@pytest_asyncio.fixture
async def mock_container():
    """Create a mock container with async mount method"""
    container = MagicMock(spec=Container)
    container.mount = AsyncMock()
    container.refresh = MagicMock()
    return container


@pytest.fixture
def mock_installer_dir(tmp_path):
    """Create a temporary directory with mock installer files"""
    installer_dir = tmp_path / "AD24"
    installer_dir.mkdir(parents=True)

    # Create mock installer files with different versions
    installers = [
        "AltiumDesignerSetup_21.0.exe",
        "AltiumDesignerSetup_22.0.exe",
        "AltiumDesignerSetup_24.0.exe",
    ]

    for installer in installers:
        (installer_dir / installer).write_bytes(b"mock installer content")

    return installer_dir


@pytest.mark.asyncio
async def test_install_altium_success(mock_container, mock_installer_dir):
    """Test successful Altium installation"""
    with patch(
        "src.interfaces.HW_Entwicklung.Altium.install.ALTIUM_INSTALLER_PATH",
        mock_installer_dir,
    ), patch("subprocess.run") as mock_run, patch(
        "src.interfaces.HW_Entwicklung.Altium.install.safe_copy_file", AsyncMock()
    ) as mock_copy:
        await install_altium(mock_container)

        # Verify file copy was called
        mock_copy.assert_called_once()

        # Verify installer was executed
        mock_run.assert_called_once()
        cmd_args = mock_run.call_args[0][0]
        assert cmd_args[0:2] == ["cmd", "/c"]
        assert "AltiumDesignerSetup_24.0.exe" in cmd_args[2]


def test_get_installer_path(mock_installer_dir):
    """Test installer path resolution"""
    with patch(
        "src.interfaces.HW_Entwicklung.Altium.install.ALTIUM_INSTALLER_PATH",
        mock_installer_dir,
    ):
        installer_path = get_installer_path()

        assert installer_path is not None
        assert installer_path.name == "AltiumDesignerSetup_24.0.exe"


def test_get_installer_path_empty_dir(tmp_path):
    """Test installer path resolution with empty directory"""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    with patch(
        "src.interfaces.HW_Entwicklung.Altium.install.ALTIUM_INSTALLER_PATH", empty_dir
    ):
        installer_path = get_installer_path()
        assert installer_path is None


@pytest.mark.asyncio
async def test_install_altium_copy_error(mock_container, mock_installer_dir):
    """Test handling of file copy errors"""

    async def mock_copy_error(*args, **kwargs):
        raise OSError("Copy failed")

    with patch(
        "src.interfaces.HW_Entwicklung.Altium.install.ALTIUM_INSTALLER_PATH",
        mock_installer_dir,
    ), patch(
        "src.interfaces.HW_Entwicklung.Altium.install.safe_copy_file", mock_copy_error
    ), pytest.raises(
        IOError
    ):
        await install_altium(mock_container)


@pytest.mark.asyncio
async def test_install_altium_subprocess_error(mock_container, mock_installer_dir):
    """Test handling of subprocess execution errors"""

    def mock_run_error(*args, **kwargs):
        raise subprocess.SubprocessError("Installation failed")

    with patch(
        "src.interfaces.HW_Entwicklung.Altium.install.ALTIUM_INSTALLER_PATH",
        mock_installer_dir,
    ), patch(
        "src.interfaces.HW_Entwicklung.Altium.install.safe_copy_file", AsyncMock()
    ), patch(
        "subprocess.run", mock_run_error
    ), pytest.raises(
        subprocess.SubprocessError
    ):
        await install_altium(mock_container)


@pytest.mark.asyncio
async def test_install_altium_refresh_and_sleep(mock_container, mock_installer_dir):
    """Test that container refresh and sleep are called"""
    with patch(
        "src.interfaces.HW_Entwicklung.Altium.install.ALTIUM_INSTALLER_PATH",
        mock_installer_dir,
    ), patch("subprocess.run"), patch(
        "src.interfaces.HW_Entwicklung.Altium.install.safe_copy_file", AsyncMock()
    ), patch(
        "asyncio.sleep", AsyncMock()
    ) as mock_sleep:
        await install_altium(mock_container)

        # Verify refresh was called
        mock_container.refresh.assert_called_once()

        # Verify sleep was called with correct duration
        mock_sleep.assert_called_once_with(1)
