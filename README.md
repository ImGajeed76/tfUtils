# TF Utils

A user-friendly tool that helps TFBern students manage their projects more efficiently. Perfect for both beginners and advanced users!

## 🎯 What is TF Utils?

TF Utils is an **unofficial** student-created tool that makes working with TFBern projects easier. It automates common tasks and helps you follow best practices, saving you time and reducing errors.

> 🎓 **Made by Students, for Students**: While this isn't an official TFBern tool, it's designed specifically to help fellow students with their project workflow.

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

> This section is for developers who want to contribute or modify the code.

### Prerequisites
- Python 3.10 - 3.12
- Poetry (package manager)
- Git
- Inno Setup (for building installers)

### Development Setup & Workflow

1. **Initial Setup**
```bash
# Clone and setup project
git clone https://github.com/ImGajeed76/tfUtils.git
cd tfUtils
poetry install
poetry run pre-commit install
```

2. **Development Process**
```bash
# Run the program locally
poetry run python main.py

# Test your changes as you develop
```

3. **Contributing Changes**
```bash
# Create a new branch
git checkout -b feature/my-new-feature

# Make your changes...

# Run pre-commit checks (REQUIRED)
poetry run pre-commit run --all-files

# Commit and push
git add .
git commit -m "feat: add my new feature"
git push origin feature/my-new-feature
```

4. **Pull Request Process**
- Create a Pull Request on GitHub
- Wait for code review
- Make requested changes if needed
- Once approved, your changes will be merged!

### Project Structure
```
tfUtils/
├── src/
│   ├── interfaces/    # Command implementations
│   │   └── ...
│   └── lib/          # Core utilities
│       ├── console.py  # User interaction
│       ├── utils.py    # File operations
│       └── paths.py    # Path handling
├── build.py          # Build script
├── main.py          # Entry point
└── pyproject.toml   # Project config
```

### Creating New Features

TF Utils uses a simple plugin system based on Python decorators. Any function with the `@interface` decorator in the `interfaces/` directory becomes available in the menu automatically!

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
@interface(name: str, activate: bool = True)
"""Mark and name interface functions for the menu system."""
```

### Code Quality

We use these tools to maintain code quality:
- `black` for formatting
- `isort` for import sorting
- `ruff` for linting
- `pre-commit` for git hooks
- `pytest` for testing

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
