# Building Your First TF Utils Interface: A Beginner's Guide

## Introduction

Welcome! This guide will walk you through creating your first TF Utils interface from scratch. Instead of jumping
straight into a complex weather app, we'll start with the basics and gradually build up our understanding.

## What is an Interface?

In TF Utils, an interface is a menu option that users can select to perform specific tasks. Think of it as adding your
own feature to the main menu. Each interface:

- Has a title that appears in the menu
- Contains a description that helps users understand what it does
- Can interact with users through the console
- Can perform various tasks when selected

## Prerequisites

- [Installation Guide](../development/getting-started.md) completed
- PyCharm installed (completed in the installation guide)
- Project opened in PyCharm (completed in the installation guide)
- Poetry environment set up (completed in the installation guide)

## Part 1: Creating Your First Simple Interface

### Step 1: Create the File

1. In PyCharm's Project Explorer, find the `interfaces` folder
2. Right-click → New → Python File
3. Name it `hello.py`

### Step 2: Write the Basic Interface

Let's start with the simplest possible interface:

```python
from textual.containers import Container
from src.lib.interface import interface
from src.lib.utils import console


@interface("My First Interface")
async def hello_world(container: Container):
    """This is my first interface!"""
    await console.print(container, "Hello, World!")
```

### Step 3: Try It Out!

1. Run the application using PowerShell:

```powershell
poetry run python main.py
```

2. You should see "My First Interface" in the menu
3. Select it and watch "Hello, World!" appear!

### Understanding Each Part:

```python
@interface("My First Interface")  # This adds your function to the menu
```

- Change "My First Interface" to anything else and run again - see how the menu title changes!

```python
async def hello_world(container: Container):
    """This is my first interface!"""
```

- The docstring (text between """) appears as a description in the menu
- Try changing it and see how the description updates
- You can also use [Markdown formatting](https://www.markdownguide.org/basic-syntax/) in the docstring. It's not exactly
  rendered in the same way, but it helps to structure and colorize the text.

```python
await console.print(container, "Hello, World!")
```

- This displays text in the console area
- The `await` is needed because we're using async functions

## Part 2: Adding User Interaction

### Step 1: Update the Code

Let's modify our interface to ask for the user's name:

```python
from textual.containers import Container
from src.lib.interface import interface
from src.lib.console import ask_input
from src.lib.utils import console


@interface("Greeting Interface")
async def greet_user(container: Container):
    """
    Ask for a name and display a personalized greeting.

    ## Markdown Example:
    - Point 1
    - Point 2

    As you can see, you can use Markdown formatting in the docstring.
    """

    # Ask for user's name
    name = await ask_input(
        container,
        "What's your name?",
        "Enter your name here"
    )

    # Display the greeting
    await console.print(container, f"Hello, {name}! Nice to meet you!")
```

### Understanding New Elements:

- `ask_input` displays a text input field
- It takes three parameters:
    1. `container`: Required for the UI
    2. "What's your name?": The question shown above the input
    3. "Enter your name here": Placeholder text in the input field

### Try These Variations:

1. Add color to your output:

```python
await console.print(container, f"[green]Hello, {name}![/green]")
```

2. Add multiple messages:

```python
await console.print(container, f"[blue]Hello, {name}![/blue]")
await console.print(container, "[yellow]Hope you're having a great day![/yellow]")
```

## Part 3: Adding Basic Logic

Let's make our interface a bit smarter:

```python
@interface("Smart Greeter")
async def smart_greet(container: Container):
    """A smarter greeting that responds differently based on the name."""

    name = await ask_input(
        container,
        "What's your name?",
        "Enter your name here"
    )

    if name.lower() == "bob":
        # we don't like bob
        return

    if name.lower() == "alice":
        await console.print(container, "[blue]Welcome back, Alice! Nice to see you again![/blue]")
    else:
        await console.print(container, f"[green]Nice to meet you, {name}![/green]")
```

### Key Concepts Demonstrated:

1. Conditional responses
2. String manipulation (`.lower()`)
3. Early exit with `return` (sorry, Bob!)
4. Adding comments for clarity

## Part 4: Practice Exercises

Try these modifications to build your understanding:

1. **Time-based Greeting:**
    - Import the `datetime` module
    - Say "Good morning", "Good afternoon", or "Good evening" based on the current time

2. **Name Length Checker:**
    - Tell users if their name is short (< 4 letters), medium (4-7 letters), or long (> 7 letters)

3. **Multiple Inputs:**
    - Ask for both first and last name
    - Combine them in the greeting

## Common Issues and Solutions

### 1. Interface Not Showing Up

- Check file is in the correct `interfaces` folder. The complete path should be `src/interfaces/hello.py`
- Verify the `@interface` decorator is properly imported and used
- Make sure function is `async`

### 2. Error Messages

- Red text indicates errors
- Use proper `await` statements
- Check all imports are correct

### 3. UI Issues

- Always run in PowerShell for best experience
- Use color codes in square brackets: `[red]`, `[blue]`, `[green]`, etc.
- See [Textual Docs](https://textual.textualize.io/) for more formatting options

## Next Steps

Now that you understand the basics, you can:

1. Try creating more complex interfaces
2. Experiment with different console colors and formatting
3. Add multiple user inputs
4. Create interfaces that perform calculations
5. Move on to the [Weather App tutorial!](weather-app.md)

Remember: The best way to learn is to experiment. Don't be afraid to modify the code and see what happens. If something
breaks, you can always go back to a working version!
