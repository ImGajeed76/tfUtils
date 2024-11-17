# Getting Started with Development

This guide will walk you through setting up your development environment for contributing to TF Utils. Whether you're
looking to fix bugs, add new features, or improve documentation, this guide will help you get started.

## Prerequisites

Before you begin, ensure you have the following tools installed on your system:

### Required Tools

- **Python**: Version 3.10
    - Download from [python.org](https://python.org)
    - Verify installation: `python --version`
- **Git**: Latest stable version
    - Download from [git-scm.com](https://git-scm.com)
    - Verify installation: `git --version`
- **Poetry**: Dependency manager
    - Download from [python-poetry.org](https://python-poetry.org)
    - Or via PowerShell:
        ```powershell
        (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
        ```
    - Verify installation: `poetry --version`

### Optional Tools

- **Inno Setup**: Only needed if you plan to build installers
    - Download from [jrsoftware.org/isinfo.php](https://jrsoftware.org/isinfo.php)
    - Required for creating Windows installers
- **PyCharm Community Edition**: IDE for Python development
    - Download from [jetbrains.com/pycharm/download](https://www.jetbrains.com/pycharm/download)
    - Recommended for easier development

## Setting Up Your Development Environment

Follow these steps to set up your local development environment:

### 1. Fork the Repository

1. Visit the [TF Utils Repository](https://github.com/ImGajeed76/tfUtils)
2. Click the "Fork" button in the top-right corner
3. Wait for GitHub to create your copy of the repository

### 2. Clone Your Fork

```bash
# Clone your forked repository
git clone https://github.com/[your-username]/tfUtils.git

# Navigate to the project directory
cd tfUtils
```

### 4. Configure Poetry

Set up Poetry for optimal usage with the project:

```bash
# Configure Poetry to create virtual environments in the project directory
poetry config virtualenvs.in-project true

# Install project dependencies
poetry install
```

### 5. Install Pre-commit Hooks

We use pre-commit hooks to ensure code quality. Install them with:

```bash
# Install pre-commit hooks
poetry run pre-commit install

# Run hooks against all files to verify installation
poetry run pre-commit run --all-files
```

## Development Tools

TF Utils uses several tools to maintain code quality:

- **Black**: Code formatter
    - Enforces consistent code style

- **isort**: Import sorter
    - Organizes import statements

- **Ruff**: Linter
    - Checks for common issues

- **pre-commit**: Git hooks
    - Runs all checks before commits
    - Automatically formats code
    - Prevents committing invalid code

## Verifying Your Setup

To ensure everything is set up correctly:

1. Run the development version:

```bash
poetry run python main.py
```

2. Check code formatting:

```bash
poetry run pre-commit run --all-files
```

## Next Steps

Now that your development environment is set up, you can:

1. Learn about our [Development Workflow](workflow.md)
2. Explore the [Project Structure](structure.md)
3. Read about [Creating Features](creating-features.md)

## Getting Help

If you encounter any issues during setup:

1. Search existing [GitHub Issues](https://github.com/ImGajeed76/tfUtils/issues)
2. Ask for help in [Discussions](https://github.com/ImGajeed76/tfUtils/discussions)
3. [Create a new issue](https://github.com/ImGajeed76/tfUtils/issues/new) if the problem persists
