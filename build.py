import os

import PyInstaller.__main__

# Build Configuration
EXECUTABLE_NAME = "utils"
OUTPUT_DIR = "output"
SRC_DIR = "src"
MAIN_SCRIPT = "main.py"


def build_executable():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(base_dir, MAIN_SCRIPT)
    src_dir = os.path.join(base_dir, SRC_DIR)
    output_dir = os.path.join(base_dir, OUTPUT_DIR)
    version_file = os.path.join(base_dir, "version_info.txt")
    icon_file = os.path.join(base_dir, "icon.ico")

    options = [
        "--noconfirm",
        "--onefile",
        "--console",
        "--clean",
        "--target-architecture",
        "x86_64",
        "--disable-windowed-traceback",
        "--version-file",
        version_file,
        "--name",
        EXECUTABLE_NAME,
        "--distpath",
        output_dir,
        "--workpath",
        os.path.join(output_dir, "build"),
        "--specpath",
        output_dir,
        "--add-data",
        f"{src_dir}{os.pathsep}src/",
        "--icon",
        icon_file,
        main_script,
    ]

    os.makedirs(output_dir, exist_ok=True)
    PyInstaller.__main__.run(options)


if __name__ == "__main__":
    build_executable()
