# Project Structure

This document explains the organization and structure of the TF Utils codebase. Understanding this structure is
essential for contributing to the project effectively.

## Overview

The TF Utils project follows a modular architecture designed for clarity and extensibility. Here's the high-level
structure:

```
tfUtils/
├── docs/              # Documentation
│   ├── development/
│   ├── index.md
│   └── ...
├── src/
│   ├── interfaces/    # Command implementations
│   │   ├── Office/    # Office-related commands
│   │   ├── Altium/    # Altium-related commands
│   │   └── ...        # Other command categories
│   └── lib/           # Core utilities
│       ├── console.py # User interaction utilities
│       ├── utils.py   # File operations
│       └── paths.py   # Path handling
├── tests/             # Test suite
│   ├── test_console.py
│   ├── test_utils.py
│   └── ...
├── build.py          # Build script
├── main.py           # Entry point
├── mkdocs.yml        # MKDocs configuration
└── pyproject.toml    # Project configuration
```

## Key Directories and Files

### `/src` Directory

The main source code directory contains all the core functionality of TF Utils.

#### `/src/interfaces`

This directory contains all the command implementations that appear in the TF Utils menu. Each file or subdirectory here
represents a menu item or category.

```
# Example interface structure
interfaces /
├── hello_world.py          # Main menu: "Say Hello"
├── new_project.py          # Main menu: "New Project"
├── Office /                # Creates "Office" submenu
│   ├── info.md             # Info page for "Office" submenu
│   ├── create_document.py  # Submenu: "Create Document"
│   └── templates.py        # Submenu: "Manage Templates"
└── Altium /                # Creates "Altium" submenu
    ├── info.md             # Info page for "Altium" submenu
    ├── create_project.py   # Submenu: "Create Project"
    └── templates.py        # Submenu: "Manage Templates"
```

The directory structure directly influences the menu hierarchy in the application. Subdirectories create submenus,
making it easy to organize related commands.

For better user experience, each folder should contain an `info.md` file with a brief description of the submenu.

#### `/src/lib`

Contains core utility functions and classes used throughout the application:

- **`console.py`**: Provides wrappers for the textual user interface
- **`utils.py`**: Provides file system operations like copying files, copying directories, downloading files, etc.
- **`paths.py`**: Manages path handling and validation for network paths

### `/tests` Directory

Contains the test suite organized to mirror the structure of the `src` directory. Each module in `src` should have a
corresponding test file.

Currently, this directory is not implemented. We plan to add tests in the future.

```
tests/
├── interfaces/
│   ├── test_hello_world.py
│   └── Office/
│       └── test_create_document.py
└── lib/
    ├── test_console.py
    ├── test_utils.py
    └── test_paths.py
```

### Root Files

- **`main.py`**: Application entry point
- **`build.py`**: Handles building the executable and installer
- **`pyproject.toml`**: Project metadata and dependencies
- **`poetry.lock`**: Locked dependencies for reproducible builds
- **`mkdocs.yml`**: Configuration for the documentation site

## Adding New Features

When adding new features to TF Utils, follow these structural guidelines:

1. **New Commands**
    - Add new command files in `/src/interfaces`
    - Use subdirectories for related command groups
    - Follow the naming convention

2. **New Utilities**
    - Add general utilities to `/src/lib/utils.py`
    - Create new modules in `/src/lib` for distinct functionality

3. **Tests**
    - Create corresponding test files in `/tests`
    - Match the source directory structure

## Module Organization

Each Python module should follow this general organization:

```python
"""Module docstring explaining purpose and usage."""

# Standard library imports
import os
import sys

# Third-party imports
import click
import rich

# Local imports
from src.lib import console
from src.lib import utils

# Constants
DEFAULT_TIMEOUT = 30
TEMPLATE_DIR = "templates"


# Classes
class MyClass:
    """Class docstring."""
    pass


# Functions
def my_function():
    """Function docstring."""
    pass
```

## Best Practices

1. **Directory Structure**
    - Keep related files together in appropriate subdirectories
    - Use clear, descriptive names for files and directories
    - Maintain parallel structure between source and tests

2. **Module Organization**
    - Follow the import order: standard library, third-party, local
    - Group related functionality together
    - Use docstrings for all modules, classes, and functions

3. **Feature Organization**
    - Place new features in appropriate subdirectories
    - Create new subdirectories for related feature groups
    - Keep interface files focused on a single responsibility

## Next Steps

- Review the [Development Workflow](workflow.md) guide
- Learn about [Creating Features](creating-features.md)
- Understand the [Key Components](components.md) of the system
