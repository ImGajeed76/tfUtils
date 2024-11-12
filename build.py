import os

import PyInstaller.__main__

# Build Configuration
EXECUTABLE_NAME = "utils"
OUTPUT_DIR = "output"  # relative to script location
SRC_DIR = "src"  # relative to script location
MAIN_SCRIPT = "main.py"  # relative to script location


def build_executable():
    # Get absolute path to script directory
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Define paths
    main_script = os.path.join(base_dir, MAIN_SCRIPT)
    src_dir = os.path.join(base_dir, SRC_DIR)
    output_dir = os.path.join(base_dir, OUTPUT_DIR)

    options = [
        "--noconfirm",
        "--onefile",
        "--console",
        "--target-architecture",
        "x86_64",  # Windows 64-bit
        "--name",
        EXECUTABLE_NAME,
        "--distpath",
        output_dir,  # Set output directory
        "--workpath",
        os.path.join(output_dir, "build"),  # Set build directory
        "--specpath",
        output_dir,  # Set spec file directory
        "--add-data",
        f"{src_dir}{os.pathsep}src/",
        main_script,
    ]

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Run PyInstaller
    PyInstaller.__main__.run(options)


if __name__ == "__main__":
    build_executable()
