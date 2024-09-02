# TF Utils

A comprehensive utility tool for streamlining project creation and management across various platforms.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
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
13. Optionally, choose whether to open your uVision project in CLion. This will copy the necessary files to the directory for easier setup.

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

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/ImGajeed76/tfUtils/issues) on my GitHub page or send an email to my GitHub email address.

## License

TF Utils is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
