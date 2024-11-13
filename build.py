import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

import PyInstaller.__main__
import tomli

# Build Configuration
EXECUTABLE_NAME = "tfutils"
OUTPUT_DIR = "dist"
SRC_DIR = "src"
MAIN_SCRIPT = "main.py"


def generate_app_manifest() -> str:
    """
    Generate Windows application manifest with proper permissions and declarations.
    """
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
    version="1.0.0.0"
    processorArchitecture="amd64"
    name="TFUtils.CLI.StudentProject"
    type="win32"
  />
  <description>TFBern Project Management CLI Tool - Open Source Student Utility</description>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="asInvoker" uiAccess="false"/>
      </requestedPrivileges>
    </security>
  </trustInfo>
  <compatibility xmlns="urn:schemas-microsoft-com:compatibility.v1">
    <application>
      <!-- Windows 10 and Windows 11 -->
      <supportedOS Id="{8e0f7a12-bfb3-4fe8-b9a5-48fd50a15a9a}"/>
    </application>
  </compatibility>
  <application xmlns="urn:schemas-microsoft-com:asm.v3">
    <windowsSettings>
      <dpiAware xmlns="http://schemas.microsoft.com/SMI/2005/WindowsSettings">true</dpiAware>
      <longPathAware xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">true</longPathAware>
    </windowsSettings>
  </application>
</assembly>
"""


def get_version_from_poetry() -> str:
    """Read version from pyproject.toml"""
    try:
        with open("pyproject.toml", "rb") as f:
            pyproject = tomli.load(f)
            return pyproject["tool"]["poetry"]["version"]
    except Exception as e:
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


def create_verification_files(build_dir: str, version: str):
    """Create verification files for the build"""
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

    # Create verification file
    verification_info = {
        "version": version,
        "build_date": datetime.now().isoformat(),
        "files": hashes,
        "build_type": "PyInstaller",
    }

    # Write JSON verification file
    verify_file = os.path.join(build_dir, "verification.json")
    with open(verify_file, "w") as f:
        json.dump(verification_info, f, indent=2)

    # Write SHA256SUMS file (traditional format)
    with open(os.path.join(build_dir, "SHA256SUMS"), "w") as f:
        for file_path, hash_info in hashes.items():
            f.write(f"{hash_info['sha256']} *{file_path}\n")


def create_inno_setup_script(version: str, base_dir: Path, output_dir: Path) -> str:
    """Generate Inno Setup script with enhanced permissions and DLL handling"""
    return f"""#define MyAppName "TFUtils CLI"
#define MyAppVersion "{version}"
#define MyAppPublisher "Student Project - TFBern"
#define MyAppURL "https://github.com/ImGajeed76/tfUtils"
#define MyAppExeName "{EXECUTABLE_NAME}.exe"

[Setup]
AppId={{{{D35A1F9C-4A95-4C2B-8235-62C4C3BE85A3}}}}
AppName={{#MyAppName}}
AppVersion={{#MyAppVersion}}
AppVerName={{#MyAppName}} {{#MyAppVersion}}
AppPublisher={{#MyAppPublisher}}
AppPublisherURL={{#MyAppURL}}
AppSupportURL={{#MyAppURL}}
AppUpdatesURL={{#MyAppURL}}
DefaultDirName={{userpf}}\\{{#MyAppName}}
DefaultGroupName={{#MyAppName}}
AllowNoIcons=yes
LicenseFile={str(base_dir / "LICENSE")}
InfoBeforeFile={str(base_dir / "README.md")}
OutputDir={str(output_dir)}
OutputBaseFilename={EXECUTABLE_NAME}_setup_v{version}
SetupIconFile={str(base_dir / "icon.ico")}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
VersionInfoVersion={version}
VersionInfoCompany=Student Project
VersionInfoCopyright=GPL-3.0 License
VersionInfoDescription=TFBern Project Management CLI Tool
ChangesEnvironment=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "german"; MessagesFile: "compiler:Languages\\German.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"
Name: "addtopath"; Description: "Add to PATH"; GroupDescription: "System Integration:"

[Files]
Source: "{str(output_dir / EXECUTABLE_NAME / '*')}"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{str(base_dir / 'LICENSE')}"; DestDir: "{{app}}"
Source: "{str(base_dir / 'README.md')}"; DestDir: "{{app}}"
Source: "{str(output_dir / EXECUTABLE_NAME / 'verification.json')}"; DestDir: "{{app}}"
Source: "{str(output_dir / EXECUTABLE_NAME / 'SHA256SUMS')}"; DestDir: "{{app}}"

[Dirs]
Name: "{{app}}"; Permissions: users-full

[Icons]
Name: "{{group}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"
Name: "{{group}}\\Documentation"; Filename: "{{app}}\\README.md"
Name: "{{userdesktop}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: desktopicon

[Code]
procedure EnvAddPath(Path: string);
var
    Paths: string;
begin
    if not RegQueryStringValue(HKEY_CURRENT_USER,
        'Environment',
        'Path', Paths)
    then Paths := '';

    if Pos(';' + Uppercase(Path) + ';', ';' + Uppercase(Paths) + ';') > 0 then exit;

    Paths := Paths + ';'+ Path +';'

    if RegWriteStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', Paths)
    then Log(Format('The [%s] added to PATH: [%s]', [Path, Paths]))
    else Log(Format('Error while adding the [%s] to PATH: [%s]', [Path, Paths]));
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
    if CurStep = ssPostInstall then
    begin
        if IsTaskSelected('addtopath') then
            EnvAddPath(ExpandConstant('{{app}}'));
    end;
end;
"""


def generate_runtime_hook() -> str:
    """Generate a runtime hook to help with DLL loading"""
    return """import os
import sys
import ctypes

def pre_init():
    if sys.platform == 'win32':
        # Ensure proper DLL loading
        if hasattr(sys, 'frozen'):
            # Get the directory where the exe is located
            exe_dir = os.path.dirname(sys.executable)

            # Add the exe directory to PATH
            os.environ['PATH'] = exe_dir + os.pathsep + os.environ.get('PATH', '')

            # Add _internal directory to PATH if it exists
            internal_dir = os.path.join(exe_dir, '_internal')
            if os.path.exists(internal_dir):
                os.environ['PATH'] = internal_dir + os.pathsep + os.environ['PATH']

            # Set DLL directory
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            if hasattr(kernel32, 'SetDllDirectoryW'):
                kernel32.SetDllDirectoryW(exe_dir)

pre_init()
"""


def build_executable(version: str):
    """
    Build executable using PyInstaller with enhanced security and optimization flags
    """
    base_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    main_script = base_dir / MAIN_SCRIPT
    output_dir = base_dir / OUTPUT_DIR
    work_dir = output_dir / "build"

    # Create runtime hook
    runtime_hook_path = base_dir / "runtime_hook.py"
    with open(runtime_hook_path, "w") as f:
        f.write(generate_runtime_hook())

    # Create manifest file
    manifest_path = base_dir / "app.manifest"
    with open(manifest_path, "w") as f:
        f.write(generate_app_manifest())

    # Prepare build directory
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(work_dir, exist_ok=True)

    # PyInstaller build options
    options = [
        str(main_script),
        "--name",
        EXECUTABLE_NAME,
        "--onedir",  # Better for dynamic imports
        "--console",
        "--clean",
        "--noconfirm",
        "--log-level",
        "WARN",
        "--runtime-hook",
        str(runtime_hook_path),  # Add runtime hook
        "--disable-windowed-traceback",
        "--collect-submodules=src",
        "--collect-data=src",
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
        str(manifest_path),
        "--icon",
        str(base_dir / "icon.ico"),
        # Add data files
        "--add-data",
        f"{str(base_dir / SRC_DIR)}{os.pathsep}src",
        # Optimization and security
        "--strip",  # Remove debug symbols
        "--noupx",  # Don't use UPX (can trigger AV)
    ]

    try:
        # Build with PyInstaller
        PyInstaller.__main__.run(options)

        # Create verification files
        create_verification_files(str(output_dir / EXECUTABLE_NAME), version)

        # Modify Inno Setup to ensure proper permissions
        inno_script = create_inno_setup_script(version, base_dir, output_dir)
        inno_script_path = output_dir / "installer.iss"

        with open(inno_script_path, "w") as f:
            f.write(inno_script)

        # Run Inno Setup Compiler
        subprocess.run(["iscc", str(inno_script_path)], check=True)

        # Clean up temporary files
        manifest_path.unlink()
        runtime_hook_path.unlink()

        print("\nBuild completed successfully!")
        print(f"Executable: {output_dir / EXECUTABLE_NAME / f'{EXECUTABLE_NAME}.exe'}")
        print(f"Installer: {output_dir / f'{EXECUTABLE_NAME}_setup_v{version}.exe'}")
        print(
            f"Verification files: {output_dir / EXECUTABLE_NAME / 'verification.json'}"
        )
        print(f"                   {output_dir / EXECUTABLE_NAME / 'SHA256SUMS'}")

    except Exception as e:
        print(f"Error during build process: {e}")
        import traceback

        print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    version = get_version_from_poetry()
    print(f"Building TFUtils v{version}")
    print("=" * 50)
    build_executable(version)
