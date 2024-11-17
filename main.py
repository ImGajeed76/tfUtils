import sys
from pathlib import Path

from src.lib.interface_loader import (
    create_folder_references,
    create_interface_references,
    scan_interfaces,
)
from src.lib.interface_viewer import InterfaceViewer

root_folder = Path(__file__).parent
interface_folder = root_folder / Path("src/interfaces")
src_folder = root_folder / Path("src")


def main():
    interfaces = scan_interfaces(interface_folder, src_folder)

    references = create_interface_references(interfaces)
    references.extend(create_folder_references(interfaces, interface_folder))

    app = InterfaceViewer("TF Utils", references)
    app.run()
    sys.exit(app.return_code or 0)


if __name__ == "__main__":
    main()
