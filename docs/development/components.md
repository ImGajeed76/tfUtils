# Core Components

TF Utils is built on several key components that work together to provide a robust and user-friendly interface. This document details the core components and their usage.

## Interface Decorator

The interface decorator is the primary way to create new commands in TF Utils. It uses Textual for the UI and supports async operations.

```python
from textual.containers import Container
from src.lib.interface import interface

@interface("Command Name", activate=True)
async def my_command(container: Container):
    """
    Your command implementation here.
    """
    pass
```

### Parameters

- `name`: The name that will appear in the menu
- `activate`: Boolean or callable that determines if the command should be active

### Example

```python
@interface("Neuen Obsidian Vault erstellen")
async def create_new_obsidian_vault(container: Container):
    """
    Creates a new Obsidian vault with preconfigured settings and plugins.

    This command will:
    1. Ask for the vault name
    2. Create the directory
    3. Copy template files
    4. Set up recommended plugins
    """
    vault_name = await ask_input(
        container,
        "Vault Name",
        "Wie soll dein neuer Vault heißen?"
    )

    # Implementation details...
```

## Console Utilities

The console module provides user interaction components built on Textual. These components offer a consistent, user-friendly interface for common operations.

### ask_input

Prompts the user for text input with optional validation.

```python
async def ask_input(
    container: Container,
    question: str,
    placeholder: str = "",
    password: bool = False,
    regex: str = r"[\u0000-\uFFFF]*",
    # ... other options
) -> str
```

#### Example Usage

```python
name = await ask_input(
    container,
    "Enter project name",
    placeholder="MyProject",
    regex=r"[A-Za-z0-9_-]+"
)
```

### ask_yes_no

Creates a Yes/No prompt with keyboard shortcuts.

```python
async def ask_yes_no(
    container: Container,
    question: str,
    yes_text: str = "Yes",
    no_text: str = "No",
    default: bool = True
) -> bool
```

#### Example Usage

```python
if await ask_yes_no(container, "Create backup before proceeding?"):
    # Handle yes case
```

### ask_select

Creates a selection menu from a list of options.

```python
async def ask_select(
    container: Container,
    question: str,
    options: list[str]
) -> str
```

#### Example Usage

```python
template = await ask_select(
    container,
    "Select project template",
    ["Basic", "Advanced", "Custom"]
)
```

## File System Operations

The utils module provides robust file system operations with progress tracking and error handling.

### Key Features

- Asynchronous file operations
- Progress bars for long operations
- Concurrent file copies
- Network path support
- Error handling and recovery

### Common Operations

```python
# Copy a single file
await safe_copy_file(container, source, destination)

# Copy entire directory
await safe_copy_directory(container, source, destination)

# Download file from URL
await safe_download(container, url, destination)

# List files in directory
files = await get_copied_files(container, directory)
```

### Progress Tracking

File operations automatically show progress using Textual's progress bars:

```python
async def copy_large_directory(container: Container):
    await safe_copy_directory(
        container,
        source="./template",
        destination="./new_project",
        max_concurrent_copies=5  # Adjust for performance
    )
```

## Network Path Handling

TF Utils includes special handling for Windows network paths through the `NetworkPath` class.

### Features

- Automatic drive letter remapping
- Support for common TFBern network shares
- Path validation
- Fallback mechanisms

### Network Share Mappings

```python
_network_mappings = {
    "T:": "t_lernende",
    "N:": "n_home-s",
    "S:": "s_mitarbeiter",
    "U:": "u_archiv",
}
```

### Usage Example

```python
from src.lib.paths import NetworkPath

# Automatically handles remapping
path = NetworkPath("T:\\my_project")
if path.is_valid:
    # Use the path
```

## Error Handling

The system includes comprehensive error handling with user-friendly messages:

```python
try:
    await safe_copy_directory(container, source, dest)
except Exception as e:
    await container.mount(Label(f"[red]Error: {str(e)}[/red]"))
```

## Best Practices

1. **Always Use Async/Await**
   ```python
   @interface("My Command")
   async def my_command(container: Container):
       # Use async operations
   ```

2. **Progress Feedback**
   ```python
   await console.print(container, "[blue]Processing...[/blue]")
   # ... operation ...
   await console.print(container, "[green]Complete![/green]")
   ```

3. **Error Handling**
   ```python
   try:
       result = await operation()
   except Exception as e:
       await console.print(container, f"[red]Error: {str(e)}[/red]")
   ```

4. **Input Validation**
   ```python
   name = await ask_input(
       container,
       "Enter name",
       regex=r"^[A-Za-z0-9_-]+$"
   )
   ```

5. **Network Path Handling**
   ```python
   path = NetworkPath(user_input)
   if not path.is_valid:
       await console.print(container, "[red]Invalid network path[/red]")
   ```

## Contributing New Components

When adding new components:

1. Place them in the appropriate module:
   - User interaction → `console.py`
   - File operations → `utils.py`
   - Path handling → `paths.py`
   - New commands → `interfaces/`

2. Follow the async pattern:
   ```python
   async def new_component(container: Container, ...):
       # Implementation
   ```

3. Include proper error handling and progress feedback

4. Add docstrings with examples:
   ```python
   def my_function():
       """
       Component description.

       Example:
       ```python
       result = await new_component(container)
       ```
       """
       pass
   ```
