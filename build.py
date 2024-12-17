# new build script for tfutils
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import jinja2
import PyInstaller.__main__
import tomli

# Build Configuration from pyproject.toml
with open("pyproject.toml", "rb") as f:
    PYPROJECT = tomli.load(f)

APP_CONFIG = PYPROJECT.get("tool", {}).get("tfutils", {})
EXECUTABLE_NAME = APP_CONFIG.get("executable_name", "tfutils")
APP_ID = APP_CONFIG.get("app_id", "{e3aa761f-58e4-4d53-9c37-75f86cbef4d0}")
OUTPUT_DIR = "dist"
SRC_DIR = "src"
MAIN_SCRIPT = "main.py"
TEMPLATE_DIR = Path("build_templates")


def setup_jinja_env() -> jinja2.Environment:
    """Setup Jinja2 environment with template directory"""
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )


def get_version_from_poetry() -> str:
    """Read version from pyproject.toml"""
    try:
        return PYPROJECT["tool"]["poetry"]["version"]
    except KeyError as e:
        print(f"Error reading version from pyproject.toml: {e}")
        return "1.0.0"


def calculate_file_hash(filepath: str) -> Dict[str, str]:
    """Calculate SHA-256 and MD5 hashes for a file"""
    sha256_hash = hashlib.sha256()
    md5_hash = hashlib.md5()

    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
            md5_hash.update(chunk)

    return {"sha256": sha256_hash.hexdigest(), "md5": md5_hash.hexdigest()}


def create_verification_files(
    build_dir: str, version: str, installer_path: Path | None = None
):
    """Create verification files for the build including installer hash if available"""
    files_to_verify = []
    hashes = {}

    # Calculate hashes for all relevant files
    for root, _, files in os.walk(build_dir):
        for file in files:
            if file.endswith((".exe", ".dll", ".pyd")):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, build_dir)
                files_to_verify.append(rel_path)
                hashes[rel_path] = calculate_file_hash(filepath)

    # Add installer hash if available
    if installer_path and installer_path.exists():
        installer_hash = calculate_file_hash(str(installer_path))
        hashes[installer_path.name] = installer_hash

    # Create verification file
    verification_info = {
        "version": version,
        "build_date": datetime.now().isoformat(),
        "files": hashes,
        "build_type": "PyInstaller",
        "target_platform": "Windows 10/11 x64",
    }

    # Write JSON verification file
    verify_file = os.path.join(build_dir, "verification.json")
    with open(verify_file, "w") as f:
        json.dump(verification_info, f, indent=2)

    # Write SHA256SUMS.txt file
    with open(os.path.join(build_dir, "SHA256SUMS.txt"), "w") as f:
        for file_path, hash_info in hashes.items():
            f.write(f"{hash_info['sha256']} *{file_path}\n")


def get_pyinstaller_excludes() -> List[str]:
    """Get list of packages to exclude from build"""
    return [
        "src/tests",  # Exclude test files
        "pytest",
        "test",
        "tests",
        "_pytest",
    ]


def get_pyproject_dependencies_for_pyinstaller() -> List[str]:
    """Get list of dependencies from pyproject.toml"""
    dependencies = PYPROJECT["tool"]["poetry"]["dependencies"].keys()
    collect_all = []
    for dep in dependencies:
        collect_all.extend(["--collect-all", dep])
    return collect_all


def copy_required_files(base_dir: Path, output_dir: Path):
    """Copy required files from project root to output directory"""
    files_to_copy = ["LICENSE", "README.md", "icon.ico"]

    for file in files_to_copy:
        src = base_dir / file
        dst = output_dir / EXECUTABLE_NAME / file
        if src.exists():
            import shutil

            shutil.copy2(src, dst)
            print(f"Copied {file} to {dst}")
        else:
            print(f"Warning: {file} not found in project root")


def build_executable(version: str):
    """Build executable using PyInstaller with enhanced security and optimization flags"""
    base_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    main_script = base_dir / MAIN_SCRIPT
    output_dir = base_dir / OUTPUT_DIR
    work_dir = output_dir / "build"

    # Setup Jinja2 environment
    jinja_env = setup_jinja_env()

    # Generate files from templates
    templates = {
        "runtime_hook.py.j2": {"context": {}},
        "app.manifest.j2": {"context": {"app_id": APP_ID, "version": version}},
        "installer.iss.j2": {
            "context": {
                "version": version,
                "executable_name": EXECUTABLE_NAME,
                "app_id": APP_ID,
                "src": str(output_dir / EXECUTABLE_NAME),
                "output_dir": str(output_dir),
                "product_name": APP_CONFIG.get("product_name", "TFUtils CLI"),
                "company_name": APP_CONFIG.get(
                    "company_name", "Student Project - TFBern"
                ),
                "product_description": APP_CONFIG.get(
                    "product_description", "TFBern Project Management CLI Tool"
                ),
                "github_repo": APP_CONFIG.get(
                    "github_repo", "https://github.com/ImGajeed76/tfUtils"
                ),
                "br": "{",
                "bl": "}",
            }
        },
    }

    # Prepare build directory
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(work_dir, exist_ok=True)

    generated_files = {}
    for template_name, config in templates.items():
        template = jinja_env.get_template(template_name)
        output_path = work_dir / template_name.replace(".j2", "")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(template.render(**config["context"]))
        generated_files[template_name.replace(".j2", "")] = output_path

    # PyInstaller build options
    options = [
        str(main_script),
        "--name",
        EXECUTABLE_NAME,
        "--onedir",
        "--console",
        "--clean",
        "--noconfirm",
        "--log-level",
        "WARN",
        "--runtime-hook",
        str(generated_files["runtime_hook.py"]),
        "--disable-windowed-traceback",
        "--collect-submodules=src",
        "--collect-data=src",
        # Collect packages
        *get_pyproject_dependencies_for_pyinstaller(),
        # Add runtime hooks for DLL loading
        "--hidden-import=ctypes",
        "--hidden-import=win32ctypes.core",
        # Paths
        "--distpath",
        str(output_dir),
        "--workpath",
        str(work_dir),
        "--specpath",
        str(output_dir),
        # Windows specific
        "--version-file",
        str(base_dir / "version_info.rc"),
        "--manifest",
        str(generated_files["app.manifest"]),
        "--icon",
        str(base_dir / "icon.ico"),
        # Add data files
        "--add-data",
        f"{str(base_dir / SRC_DIR)}{os.pathsep}src",
        # Optimization and security
        "--strip",
        "--noupx",
        # Target only x64 Windows 10/11
        "--target-arch",
        "x64",
        # C++ Binarys
        "--add-binary",
        r"C:\Windows\System32\vcruntime140.dll;.",
        "--add-binary",
        r"C:\Windows\System32\msvcp140.dll;.",
    ]

    # Add excludes
    for exclude in get_pyinstaller_excludes():
        options.extend(["--exclude-module", exclude])

    try:
        # Build with PyInstaller
        PyInstaller.__main__.run(options)

        # Copy LICENSE, README.md, and other required files
        copy_required_files(base_dir, output_dir)

        # Create verification files (without installer hash)
        create_verification_files(str(output_dir / EXECUTABLE_NAME), version)

        # Run Inno Setup Compiler
        inno_script_path = generated_files["installer.iss"]
        subprocess.run(["iscc", str(inno_script_path)], check=True)

        # Get installer path
        installer_path = output_dir / f"{EXECUTABLE_NAME}_setup_v{version}.exe"

        # Create verification files (including installer hash)
        create_verification_files(
            str(output_dir / EXECUTABLE_NAME), version, installer_path
        )

        # Clean up temporary files
        for file_path in generated_files.values():
            if file_path.exists():
                file_path.unlink()

        print("\nBuild completed successfully!")
        print(f"Executable: {output_dir / EXECUTABLE_NAME / f'{EXECUTABLE_NAME}.exe'}")
        print(f"Installer: {installer_path}")
        print("Verification files:")
        print(f"  - {output_dir / EXECUTABLE_NAME / 'verification.json'}")
        print(f"  - {output_dir / EXECUTABLE_NAME / 'SHA256SUMS.txt'}")

    except Exception as e:
        print(f"Error during build process: {e}")
        import traceback

        print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    version = get_version_from_poetry()
    print(f"Building {EXECUTABLE_NAME} v{version}")
    print("=" * 50)
    build_executable(version)
