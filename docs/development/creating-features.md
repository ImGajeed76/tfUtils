# Creating New Features

TF Utils uses a simple yet powerful plugin system based on Python decorators. Any function decorated with `@interface`
in the `interfaces/` directory automatically becomes available in the menu!

## Interface Structure

Each interface is an async function that receives a Textual `Container` as a parameter. This container is used for
rendering the interface elements and handling user interaction.

### Basic Interface Template

```python
from pathlib import Path
from textual.containers import Container
from src.lib.interface import interface
from src.lib.console import ask_input
from src.lib.utils import console


@interface("Your Feature Name")
async def your_feature(container: Container):
    """
    Your feature description.

    Detailed explanation of what your feature does.
    You can use markdown formatting in this docstring.

    ## Section Example:
    - Point 1
    - Point 2
    """
    # Your code here
    pass
```

## Key Components

### The Interface Decorator

```python
@interface("Display Name", activate=True)
```

- Takes a string parameter that defines how your feature appears in the menu
- Handles registration and integration with the main menu system
- Set `activate=False` to disable the feature by default
- Use `activate=True` to enable the feature by default
- `activate` can also be a function that returns a boolean

### Container Parameter

```python
async def your_feature(container: Container):
```

- The `container` parameter is a Textual UI container where your interface can render
- Used for all user interaction and display elements

### Documentation

Every interface should include a detailed docstring that:

- Explains what the feature does
- Lists any requirements or prerequisites
- Documents any special behavior or options
- Uses markdown formatting for better readability

## User Interaction Tools

### Input Prompts

```python
value = await ask_input(
    container,
    "Description or question for the user"
)
```

### Console Output

```python
await console.print(container, "[green]Success message![/green]")
await console.print(container, "[red]Error message![/red]")
```

## Complete Example

Here's a complete example that creates a new Obsidian vault with pre-configured settings:

```python
from pathlib import Path
from textual.containers import Container
from src.lib.console import ask_input
from src.lib.interface import interface
from src.lib.utils import console, safe_copy_directory


@interface("Neuen Obsidian Vault erstellen")
async def create_new_obsidian_vault(container: Container):
    """
    Erstelle einen neuen Obsidian Vault.

    Dieses Interface erstellt einen neuen Obsidian Vault im aktuellen Verzeichnis.
    Dieser neue Vault enthält bereits grundlegende Einstellungen und Plugins für
    eine bessere Obsidian-Erfahrung.

    ## Plugin Liste:
    - Excalidraw
    - Numerals
    - Better Word Count
    - OZ Calendar
    - Obsidian Banners
    - Obsidian File Cleaner
    - Quick Add
    - Table Editor
    - Code Block Customizer
    """
    # Get vault name from user
    vault_name = await ask_input(
        container, "Vault Name", "Wie soll dein neuer Vault heißen?"
    )

    # Create vault directory
    base_dir = Path().cwd()
    vault_dir = base_dir / vault_name

    # Check if directory already exists
    if vault_dir.exists():
        await console.print(container, "[red]Vault directory already exists![/red]")
        return

    # Create directory and copy template
    vault_dir.mkdir()
    current_dir = Path(__file__).parent
    obsidian_template_dir = current_dir / "ObsidianTemplate"

    await safe_copy_directory(
        container, obsidian_template_dir, vault_dir, max_concurrent_copies=20
    )

    await console.print(container, "[green]Vault created successfully![/green]")
```

## Best Practices

1. **Error Handling**
    - Always check for existing files/directories before creating them
    - Use clear error messages with appropriate colors
    - Handle exceptions gracefully

2. **User Feedback**
    - Provide clear prompts for user input
    - Show progress for long-running operations
    - Confirm successful completion

3. **Code Organization**
    - Keep interface functions focused on a single task
    - Use descriptive variable names
    - Follow the project's coding style

4. **Documentation**
    - Write clear, detailed docstrings
    - Include examples where appropriate
    - Document any assumptions or limitations

## Adding Your Feature

1. Create a new Python file in the appropriate location under `interfaces/`
2. Define your interface function with the `@interface` decorator
3. Write comprehensive docstrings
4. Implement your feature using the provided utilities
5. Test thoroughly
6. Submit a pull request

## Advanced Topics

### Concurrent Operations

When performing multiple operations (like file copies), you can use the `max_concurrent_copies` parameter to control
concurrency:

```python
await safe_copy_directory(
    container,
    source_dir,
    target_dir,
    max_concurrent_copies=20
)
```

### Nested Interfaces

You can create nested menu structures by organizing your interface files in subdirectories:

```
interfaces/
├── Office/
│   ├── word.py
│   └── excel.py
└── Development/
    ├── altium.py
    └── uvision.py
```

### Custom Utilities

If you need functionality not provided by the existing utilities, consider:

1. Adding it to the appropriate utility module
2. Creating a new utility module if it's a new category of functionality
3. Discussing with the team for larger additions

Remember to maintain backward compatibility and follow the project's coding standards when adding new utilities.
