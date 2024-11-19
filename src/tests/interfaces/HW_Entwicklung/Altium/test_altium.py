import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from textual.containers import Container

# Import the functions to test
from src.interfaces.HW_Entwicklung.Altium.altium import (
    _edit_project_files,
    _load_file_mappings,
    _rename_files,
    _update_project_vc,
    is_altium_project,
    new_altium_project,
    rename_project,
    update_project_version,
)


@pytest_asyncio.fixture
async def mock_container():
    """Create a mock container with async mount method"""
    container = MagicMock(spec=Container)
    container.mount = AsyncMock()
    return container


@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary project directory with mock Altium project files"""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()

    # Create mock project files
    project_name = "TestProject"
    version = "V1.0"

    # Create PRJPCB file
    prjpcb_file = project_dir / f"{project_name}_{version}.PRJPCB"
    prjpcb_file.write_text("Mock project content")

    # Create OutJob file
    outjob_file = project_dir / f"{project_name}_{version}.OutJob"
    outjob_file.write_text("Mock outjob content")

    # Create history file
    history_file = project_dir / "_history.txt"
    history_file.write_text("1.0\t\tTEST\t01/01/2024\tInitial Project Creation\n")

    # Create template directory
    template_dir = project_dir / "template1"
    template_dir.mkdir()
    template_prjpcb = template_dir / "Template_V1.0.PRJPCB"
    template_prjpcb.write_text("Template content")

    # Create test_input directory
    test_input_dir = project_dir / "test-input"
    test_input_dir.mkdir()
    test_input_prjpcb = test_input_dir / "test-input_V1.0.PRJPCB"
    test_input_prjpcb.write_text("Test input content")

    # Create .vc.json file
    vc_data = {
        "project_name": project_name,
        "replacements": {
            f"{project_name}_{version}.PRJPCB": "{project_name}_{project_version}.PRJPCB",  # noqa: E501
            f"{project_name}_{version}.OutJob": "{project_name}_{project_version}.OutJob",  # noqa: E501
        },
    }

    with open(project_dir / ".vc.json", "w") as f:
        json.dump(vc_data, f)

    return project_dir


@pytest_asyncio.fixture
async def mock_fs_ops():
    """Mock filesystem operations"""
    fs_ops = MagicMock()
    fs_ops.safe_copy_directory = AsyncMock()
    return fs_ops


@pytest.mark.asyncio
async def test_new_altium_project(mock_container, temp_project_dir, mock_fs_ops):
    with patch(
        "src.interfaces.HW_Entwicklung.Altium.altium.ask_input",
        return_value="test-input",
    ), patch(
        "src.interfaces.HW_Entwicklung.Altium.altium.ask_select",
        return_value="template1",
    ), patch(
        "src.interfaces.HW_Entwicklung.Altium.altium.ask_yes_no", return_value=True
    ), patch(
        "src.interfaces.HW_Entwicklung.Altium.altium.ALTIUM_TEMPLATES_PATH",
        temp_project_dir,
    ), patch(
        "src.interfaces.HW_Entwicklung.Altium.altium.Path.cwd",
        return_value=temp_project_dir,
    ), patch(
        "src.interfaces.HW_Entwicklung.Altium.altium.safe_copy_directory",
        mock_fs_ops.safe_copy_directory,
    ):
        await new_altium_project(mock_container)

        mock_fs_ops.safe_copy_directory.assert_called_once()
        assert (temp_project_dir / "test-input").exists()


@pytest.mark.asyncio
async def test_update_project_version(mock_container, temp_project_dir):
    await _update_project_vc(temp_project_dir)  # Ensure .vc.json exists

    with patch(
        "src.interfaces.HW_Entwicklung.Altium.altium.ask_input", return_value="TEST"
    ), patch("pathlib.Path.cwd", return_value=temp_project_dir):
        await update_project_version(mock_container, temp_project_dir, "V2.0")

        # Verify version update
        prjpcb_files = list(temp_project_dir.glob("*.PRJPCB"))
        assert len(prjpcb_files) == 1
        assert "TestProject_V2.0.PRJPCB" == prjpcb_files[0].name

        # Verify history update
        history_file = temp_project_dir / "_history.txt"
        assert history_file.exists()
        content = history_file.read_text()
        assert "2.0" in content


@pytest.mark.asyncio
async def test_rename_project(mock_container, temp_project_dir):
    await _update_project_vc(temp_project_dir)  # Ensure .vc.json exists
    new_name = "NewProjectName"

    with patch(
        "src.interfaces.HW_Entwicklung.Altium.altium.ask_input", return_value=new_name
    ), patch("pathlib.Path.cwd", return_value=temp_project_dir):
        await rename_project(mock_container, temp_project_dir, new_name)

        # Verify renamed files
        prjpcb_files = list(temp_project_dir.glob("*.PRJPCB"))
        assert len(prjpcb_files) == 1
        assert f"{new_name}_V1.0.PRJPCB" == prjpcb_files[0].name


def test_is_altium_project(temp_project_dir):
    with patch("pathlib.Path.cwd", return_value=temp_project_dir):
        assert is_altium_project()

    empty_dir = temp_project_dir / "empty"
    empty_dir.mkdir()
    with patch("pathlib.Path.cwd", return_value=empty_dir):
        assert not is_altium_project()


def test_load_file_mappings(temp_project_dir):
    mappings = _load_file_mappings(temp_project_dir, "NewProject", "V2.0")
    assert mappings
    assert any("NewProject_V2.0.PRJPCB" in mapping[1] for mapping in mappings)


@pytest.mark.asyncio
async def test_rename_files(temp_project_dir):
    await _update_project_vc(temp_project_dir)  # Ensure .vc.json exists
    original_file = temp_project_dir / "TestProject_V1.0.PRJPCB"
    new_name = "NewProject"
    new_version = "V2.0"

    _rename_files(temp_project_dir, new_version, new_name)

    assert not original_file.exists()
    assert (temp_project_dir / f"{new_name}_{new_version}.PRJPCB").exists()


@pytest.mark.asyncio
async def test_edit_project_files(temp_project_dir):
    await _update_project_vc(temp_project_dir)  # Ensure .vc.json exists

    new_name = "NewProject"
    new_version = "V2.0"

    file_content = "TestProject_V1.0.PRJPCB content"
    test_file = temp_project_dir / f"{new_name}_{new_version}.PRJPCB"
    test_file.write_text(file_content)

    _edit_project_files(temp_project_dir, new_version, new_name)

    with open(test_file) as f:
        new_content = f.read()
        assert "TestProject_V1.0.PRJPCB" not in new_content
        assert f"{new_name}_{new_version}.PRJPCB" in new_content


@pytest.mark.asyncio
async def test_new_altium_project_invalid_name(mock_container, temp_project_dir):
    invalid_name = "Invalid/Name"
    mock_ask_input = AsyncMock(
        side_effect=ValueError("Invalid project name"), return_value=invalid_name
    )
    mock_ask_select = AsyncMock(return_value="template1")

    with patch(
        "src.interfaces.HW_Entwicklung.Altium.altium.ask_input", mock_ask_input
    ), patch(
        "src.interfaces.HW_Entwicklung.Altium.altium.ALTIUM_TEMPLATES_PATH",
        temp_project_dir,
    ), patch(
        "src.interfaces.HW_Entwicklung.Altium.altium.ask_select", mock_ask_select
    ):
        with pytest.raises(ValueError):
            await new_altium_project(mock_container)


@pytest.mark.asyncio
async def test_update_project_version_invalid_version(mock_container, temp_project_dir):
    await _update_project_vc(temp_project_dir)  # Ensure .vc.json exists
    with patch(
        "src.interfaces.HW_Entwicklung.Altium.altium.ask_input",
        side_effect=ValueError("Invalid version format"),
    ):
        with pytest.raises(ValueError):
            await update_project_version(mock_container, temp_project_dir)
