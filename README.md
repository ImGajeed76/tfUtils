# TF Utils

A user-friendly tool that helps TFBern students manage their projects more efficiently. Perfect for both beginners and
advanced users!

## 🎯 What is TF Utils?

TF Utils is an **unofficial** student-created tool that makes working with TFBern projects easier. It automates common
tasks and helps you follow best practices, saving you time and reducing errors.

> 🎓 **Made by Students, for Students**: While this isn't an official TFBern tool, it's designed specifically to help
> fellow students with their project workflow.

## 📦 Installation Guide

### For Everyone (Quick Install)

1. Download the installer
    - Go to our [releases page](https://github.com/ImGajeed76/tfUtils/releases)
    - Click on `tfutils_setup_vX.X.X.exe` (latest version)
    - Save it to your computer

2. Install the program
    - Double-click the downloaded installer
    - Click "Next" to begin installation
    - When asked, check "Add to PATH" ✅
    - Click "Install"
    - Click "Finish"

3. Start using TF Utils
    - Restart any open command prompts or terminals
    - That's it! You're ready to go! 🎉

## 🚀 How to Use TF Utils

### Basic Usage (For Everyone)

1. **Start TF Utils**
    - Open your project folder in File Explorer
    - Click in the address bar at the top
    - Type `tfutils` and press Enter

2. **Navigate the Menu**
    - Use ↑ and ↓ arrow keys to move
    - Press Enter to select an option
    - Or just press the number shown next to your choice

### Example Menu

```
╭───────────────────────── Choose an Action: ──────────────────────────╮
│ Use arrow keys to navigate, Enter to select, or press the number key │
│                                                                      │
│    1. Altium Project                                                 │
│    2. Obsidian Notes                                                 │
│    3. Office Documents                                               │
│    4. New Project                                                    │
│ -> 5. µVision Project                                                │
╰──────────────────────────────────────────────────────────────────────╯
```

### Features

- **Project Templates**: Quickly create new projects with the correct structure
- **File Management**: Automatically organize your project files
- **Tool Integration**: Easy setup for Altium, Obsidian, Office, and µVision projects
- **Smart Prompts**: Clear instructions guide you through each step

## 🔒 Security & Trust

We take security seriously:

- ✅ No admin rights needed
- ✅ Open source - you can see all the code
- ✅ Clear build process
- ✅ SHA256 checksums provided
- ✅ Built by students like you

## 🛠️ Developer Documentation

> This section explains how to set up the development environment and contribute to TF Utils.

### Prerequisites

Before you start, make sure you have these installed:

- Python 3.10 - 3.12
- Git
- Inno Setup (only needed if you want to build installers)

### Getting Started

1. **Fork the Repository**
    - Go to [TF Utils Repository](https://github.com/ImGajeed76/tfUtils)
    - Click the "Fork" button in the top-right corner
    - This creates your own copy of the repository

2. **Clone Your Fork**
   ```bash
   git clone https://github.com/[your-username]/tfUtils.git
   cd tfUtils
   ```

3. **Install Poetry (Package Manager)**
   ```bash
   # Windows (PowerShell)
   (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -

   # Linux/MacOS/WSL
   curl -sSL https://install.python-poetry.org | python3 -
   ```

4. **Set Up Development Environment**
   ```bash
   # Install project dependencies
   poetry install

   # Install pre-commit hooks
   poetry run pre-commit install
   ```

### Development Workflow

1. **Create a Feature Branch**
   ```bash
   # Create and switch to a new branch
   git checkout -b feature/my-new-feature
   ```

2. **Make Your Changes**
    - Write your code
    - Add new tests if needed
    - Update documentation if needed

3. **Test Your Changes**
   ```bash
   # Run the program locally
   poetry run python main.py

   # Run pre-commit checks (REQUIRED)
   poetry run pre-commit run --all-files
   ```

4. **Commit and Push**
   ```bash
   # Add your changes
   git add .

   # Commit with a descriptive message
   git commit -m "feat: add my new feature"

   # Push to your fork
   git push origin feature/my-new-feature
   ```

5. **Create a Pull Request**
    - Go to the original [TF Utils Repository](https://github.com/ImGajeed76/tfUtils)
    - Click "Pull requests"
    - Click "New Pull Request"
    - Choose your feature branch
    - Fill in the description of your changes
    - Submit the pull request

6. **Review Process**
    - Wait for code review
    - Make any requested changes
    - Push new commits to your feature branch if needed
    - Once approved, your changes will be merged!

### Project Structure

```
tfUtils/
├── src/
│   ├── interfaces/    # Command implementations
│   │   └── ...
│   └── lib/           # Core utilities
│       ├── console.py  # User interaction
│       ├── utils.py    # File operations
│       └── paths.py    # Path handling
├── build.py          # Build script
├── main.py           # Entry point
└── pyproject.toml    # Project config
```

### Creating New Features

TF Utils uses a simple plugin system based on Python decorators. Any function with the `@interface` decorator in
the `interfaces/` directory becomes available in the menu automatically!

#### Examples

1. **Simple Command**

```python
# interfaces/hello_world.py
from src.lib.console import ask_input
from src.interfaces import interface


@interface(name="Say Hello")
def say_hello():
    """A simple greeting command."""
    name = ask_input("What's your name?", "Enter your name to get a greeting")
    print(f"Hello {name}!")
```

2. **Subcategory Command**

```python
# interfaces/Office/create_document.py
from src.lib.console import ask_select, ask_input
from src.lib.utils import safe_copy_file
from src.interfaces import interface


@interface(name="Create Document")
def create_doc():
    """Create a new Office document from template."""
    # Show template selection
    templates = ["Letter", "Report", "Presentation"]
    choice = ask_select("Choose template:", templates)

    # Get document name
    doc_name = ask_input(
        "Document name:",
        "Enter name for your new document",
        placeholder="My Document"
    )

    # Copy template
    template_path = f"templates/office/{templates[choice].lower()}.docx"
    safe_copy_file(template_path, f"{doc_name}.docx")
```

The file structure determines the menu structure:

```
interfaces/
├── hello_world.py          → Main menu: "Say Hello"
└── Office/                 → Creates "Office" submenu
    └── create_document.py  → Submenu item: "Create Document"
```

### Key Components

#### Console Utilities (`console.py`)

```python
def ask_select(prompt: str, choices: list[str], default: int = 0) -> int:
    """Display an interactive selection menu."""


def ask_input(question: str, description: str, placeholder: str = "",
              regex: str = None, error_message: str = None) -> str:
    """Display an interactive text input prompt with validation."""


def ask_yes_no(question: str, description: str = "") -> bool:
    """Display an interactive Yes/No selection menu."""
```

#### File Operations (`utils.py`)

```python
def safe_copy_file(source: PathLike, destination: PathLike) -> None:
    """Safely copy a file with error handling."""


def safe_copy_directory(source: PathLike, destination: PathLike) -> None:
    """Safely copy a directory with error handling."""


def get_copied_files(directory: PathLike) -> List[Path]:
    """Get list of files in a directory."""


def safe_download(url: str, destination: PathLike) -> Tuple[Optional[Path], Optional[str]]:
    """Safely download a file with error handling."""
```

#### Path Handling (`paths.py`)

```python
class NetworkPath:
    """Handle Windows network paths with validation."""
```

#### Interface Decorator

```python
@interface(name

: str, activate: bool = True)
"""Mark and name interface functions for the menu system."""
```

### Code Quality

We use these tools to maintain code quality:

- `black` for formatting
- `isort` for import sorting
- `ruff` for linting
- `pre-commit` for git hooks

### Building from Source

```bash
poetry run python build.py
# Creates installer in dist/tfutils_setup_v[version].exe
```

## 💬 Support & Community

Need help? We're here:

- 📝 [Report Issues](https://github.com/ImGajeed76/tfUtils/issues)
- 💡 [Join Discussions](https://github.com/ImGajeed76/tfUtils/discussions)
- 📧 Contact: [ImGajeed76](mailto:github.staging362@passmail.net)

## 📄 License

TF Utils is licensed under the GNU GPL v3.0. This means you can:

- ✅ Use the software for any purpose
- ✅ Study how it works and modify it
- ✅ Share the software with others
- ✅ Share your modifications

[Full License Text](LICENSE)
