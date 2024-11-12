# TF Utils

A comprehensive utility tool for streamlining project creation and management across various platforms.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Development](#development)
- [Support](#support)
- [License](#license)
- [Contributing](#contributing)

## Installation

1. Download the latest release from [release page](https://github.com/ImGajeed76/tfUtils/releases).
2. Create a new folder: `C:\Program Files\tfutils`
3. Move the downloaded executable file into the newly created folder.
4. Add the installation directory to your system's PATH:

- Press `Win + X` and select "System"
- Click on "Advanced system settings"
- Click on "Environment Variables"
- Under "System variables", find and select "Path", then click "Edit"
- Click "New" and add `C:\Program Files\tfutils`
- Click "OK" to close all dialogs

## Usage

### Creating a new uVision project

1. Create a new folder for your project (e.g., "test").
2. Open the folder in Windows Explorer.
3. Click on the address bar at the top and type `utils`. A command prompt window will open.
4. The prompt will ask if you are in the correct path. Ensure the displayed path is where you want your uVision project.
5. Type 'y' and press Enter to confirm.
6. A menu will appear with several options:

```
╭───────────────────────── Wähle eine Aktion: ──────────────────────────╮
│ Use arrow keys to navigate, Enter to select, or press the number key. │
│                                                                       │
│    1. Altium                                                          │
│    2. Obsidian                                                        │
│    3. Office                                                          │
│    4. Projekt                                                         │
│ -> 5. uVision                                                         │
╰───────────────────────────────────────────────────────────────────────╯
```

7. Select "uVision" using arrow keys or by pressing '5'.
8. Choose "neues uVision projekt" (new uVision project).
9. Select a microcontroller template (e.g., "C8051F320").
10. Name your project (e.g., "MyProject"). Avoid using spaces in the name.
11. Choose whether to create a new folder named after your project inside the current directory.
12. Press Enter to select the default version number.
13. Optionally, choose whether to open your uVision project in CLion. This will copy the necessary files to the
    directory for easier setup.

Your new uVision project is now created and ready to use!

## Features

### Project Creation

- Create new Altium projects
- Create new uVision projects
- Set up Obsidian vaults (with pre-installed add-ons like Excalidraw)
- Generate general project structures

### Project Management

- Manage Altium projects:
    - Rename projects
    - Reversion projects
- Create schema and layout checklists
- Set up default project structures with necessary components

## Development

### Prerequisites

- Python 3.10 - 3.12
- Poetry (for dependency management)
- Git

The project uses the following code quality tools:

- black (code formatting)
- isort (import sorting)
- ruff (linting)
- pre-commit (automated checks)

Dependencies:

- rich
- tqdm

Development dependencies:

- pre-commit
- pyinstaller

### Setting up the development environment

1. Clone the repository:

```bash
git clone https://github.com/ImGajeed76/tfUtils.git
cd tfUtils
```

2. Install dependencies using Poetry:

```bash
poetry install
```

3. Set up pre-commit hooks:

```bash
poetry run pre-commit install
```

### Building the project

To build the project, run:

```bash
poetry run python build.py
```

### Before committing

Always run pre-commit before pushing your changes:

```bash
poetry run pre-commit run --all-files
```

### Adding Custom Functions

You can extend TF Utils with your own functions. Here's how:

1. Create a new file in the `src/interfaces` folder or any subfolder. The subfolder structure defines the TUI menu
   hierarchy.
   For example:
    - `src/interfaces/myInterface/my_app.py` will create a menu option "myInterface" with your function inside
    - `src/interfaces/my_app.py` will put your function in the root menu

2. In your new file (e.g., `my_app.py`), create a function with the `@interface` decorator:

```python
from src.lib.interface import interface


@interface("My App")  # "My App" is what users will see in the menu
def my_app():
    print("Hello World")
    input()
```

3. Run the program to see your new function:

```bash
poetry run python main.py
```

Your function "My App" will now appear in the TUI menu structure based on its file location.

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/ImGajeed76/tfUtils/issues) on
my GitHub page or send an email to my GitHub email address.

## License

TF Utils is licensed under the GNU General Public License v3.0 (GPL-3.0).

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not,
see <https://www.gnu.org/licenses/>.
