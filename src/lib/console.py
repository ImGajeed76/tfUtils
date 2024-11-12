"""Command line interface utilities for handling user input with rich formatting.

This module provides a set of functions for creating interactive command line interfaces
with rich text formatting, cursor manipulation, and user input handling.
"""

import enum
import msvcrt
import re
import sys
import time
from dataclasses import dataclass
from typing import Generic, Optional, TypeVar

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

T = TypeVar("T")


class KeyCode(enum.Enum):
    """Enum representing common key codes."""

    ENTER = b"\r"
    ESC = b"\x1b"
    CTRL_C = b"\x03"
    BACKSPACE = b"\x08"
    ARROW_PREFIX = b"\xe0"
    UP_ARROW = b"H"
    DOWN_ARROW = b"P"
    LEFT_ARROW = b"K"
    RIGHT_ARROW = b"M"
    DELETE = b"S"


@dataclass
class InputConfig:
    """Configuration for input handling."""

    max_length: int = 36
    cursor_blink_interval: float = 0.5
    cpu_sleep_interval: float = 0.01


class CursorManager:
    """Context manager for handling cursor visibility."""

    @staticmethod
    def hide():
        """Hide the cursor."""
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

    @staticmethod
    def show():
        """Show the cursor."""
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

    def __enter__(self):
        self.hide()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.show()


class InputHandler(Generic[T]):
    """Base class for handling different types of input."""

    def __init__(self, console: Console):
        self.console = console

    def handle_key(self, key: bytes) -> Optional[T]:
        """Handle a keypress and return a value if input is complete."""
        if key == KeyCode.ESC.value or key == KeyCode.CTRL_C.value:
            raise KeyboardInterrupt
        return None


class MenuHandler(InputHandler[int]):
    """Handler for menu selection input."""

    def __init__(self, console: Console, choices: list[str], selected: int):
        super().__init__(console)
        self.choices = choices
        self.selected = selected

    def print_menu(self, prompt: str):
        """Print the menu with the current selection."""
        menu = [
            "[italic]"
            "Use arrow keys to navigate, "
            "Enter to select, "
            "or press the number key."
            "[/italic]",
            "",
        ]
        for i, choice in enumerate(self.choices):
            prefix = "-> " if i == self.selected else "   "
            style = "[bold cyan]" if i == self.selected else ""
            menu.append(
                f"{style}{prefix}{i + 1}. {choice}{('[/bold cyan]' if style else '')}"
            )

        self.console.print(Panel("\n".join(menu), title=prompt, expand=False))

    def handle_key(self, key: bytes) -> Optional[int]:
        """Handle menu navigation and selection."""
        if key == KeyCode.ENTER.value:
            return self.selected
        elif key == KeyCode.ARROW_PREFIX.value:
            arrow_key = msvcrt.getch()
            if arrow_key == KeyCode.UP_ARROW.value and self.selected > 0:
                self.selected -= 1
            elif (
                arrow_key == KeyCode.DOWN_ARROW.value
                and self.selected < len(self.choices) - 1
            ):
                self.selected += 1
        elif key in map(str.encode, "123456789"):
            index = int(key.decode()) - 1
            if 0 <= index < len(self.choices):
                return index
        return super().handle_key(key)


def ask_select(prompt: str, choices: list[str], default: int = 0) -> int:
    """Display a selection menu and return the chosen index.

    Args:
        prompt: The prompt text to display above the menu
        choices: List of choices to display
        default: Default selected index

    Returns:
        Selected index from the choices list

    Raises:
        KeyboardInterrupt: If user cancels with Esc or Ctrl+C
    """
    console = Console()
    selected = default if 0 <= default < len(choices) else 0
    handler = MenuHandler(console, choices, selected)

    while True:
        console.clear()
        handler.print_menu(prompt)

        if msvcrt.kbhit():
            key = msvcrt.getch()
            result = handler.handle_key(key)
            if result is not None:
                return result


class TextInputState:
    """Maintains the state of text input."""

    def __init__(self, config: InputConfig):
        self.user_input: str = ""
        self.cursor_position: int = 0
        self.blink_state: bool = True
        self.last_blink: float = time.time()
        self.error: str = ""
        self.last_input_len: int = 0
        self.config = config

    def insert_char(self, char: str) -> None:
        """Insert a character at the current cursor position."""
        if len(self.user_input) < self.config.max_length:
            self.user_input = (
                self.user_input[: self.cursor_position]
                + char
                + self.user_input[self.cursor_position :]
            )
            self.cursor_position += 1

    def delete_char(self) -> None:
        """Delete the character before the cursor."""
        if self.cursor_position > 0:
            self.user_input = (
                self.user_input[: self.cursor_position - 1]
                + self.user_input[self.cursor_position :]
            )
            self.cursor_position -= 1

    def forward_delete_char(self) -> None:
        """Delete the character at the cursor."""
        if self.cursor_position < len(self.user_input):
            self.user_input = (
                self.user_input[: self.cursor_position]
                + self.user_input[self.cursor_position + 1 :]
            )


class TextInputHandler(InputHandler[str]):
    """Handler for text input."""

    def __init__(
        self,
        console: Console,
        state: TextInputState,
        placeholder: str = "",
        regex: Optional[str] = None,
        error_message: Optional[str] = None,
    ):
        super().__init__(console)
        self.state = state
        self.placeholder = placeholder
        self.regex = regex
        self.error_message = error_message

    def print_input(self, question: str, description: str) -> None:
        """Print the current input state."""
        input_text = Text()
        if self.state.user_input:
            input_text.append(self.state.user_input)
        else:
            input_text.append(f"[bright_black]{self.placeholder}[/bright_black]")

        content = (
            f"{description}\n\n{input_text}\n\n"
            f"[blue]Press Enter to submit, Esc to cancel[/blue]"
        )
        if self.state.error:
            content += f"\n\n[bold red]{self.state.error}[/bold red]"

        self.console.print(
            Panel(content, title=f"[green]{question}[/green]", expand=False)
        )

    def update_cursor(self, force_blink_state: Optional[bool] = None) -> None:
        """Update the cursor display."""
        current_time = time.time()
        if force_blink_state is not None:
            self.state.blink_state = force_blink_state
        elif (
            current_time - self.state.last_blink
            > self.state.config.cursor_blink_interval
        ):
            self.state.blink_state = not self.state.blink_state
            self.state.last_blink = current_time

        # Clear the line and reposition cursor
        sys.stdout.write("\r\033[2C")
        sys.stdout.write(" " * self.state.last_input_len)
        sys.stdout.write("\r\033[2C")

        # Write the input text with cursor
        sys.stdout.write(self.state.user_input[: self.state.cursor_position])
        if self.state.blink_state:
            sys.stdout.write("█")
        else:
            if not self.state.user_input and self.placeholder:
                sys.stdout.write(f"\033[90m{self.placeholder[0]}\033[97m")
            else:
                sys.stdout.write(
                    self.state.user_input[self.state.cursor_position]
                    if self.state.cursor_position < len(self.state.user_input)
                    else " "
                )
        sys.stdout.write(self.state.user_input[self.state.cursor_position + 1 :])
        sys.stdout.flush()

        self.state.last_input_len = len(self.state.user_input) + 1

    def handle_key(self, key: bytes) -> Optional[str]:
        """Handle text input keys."""
        if key == KeyCode.ENTER.value:
            if self.state.user_input:
                if self.regex is None or re.match(self.regex, self.state.user_input):
                    return self.state.user_input
                self.state.error = (
                    self.error_message
                    or "Input does not match the required format. Please try again."
                )
            else:
                return self.placeholder
        elif key == KeyCode.ARROW_PREFIX.value:
            arrow_key = msvcrt.getch()
            if arrow_key == KeyCode.LEFT_ARROW.value and self.state.cursor_position > 0:
                self.state.cursor_position -= 1
            elif (
                arrow_key == KeyCode.RIGHT_ARROW.value
                and self.state.cursor_position < len(self.state.user_input)
            ):
                self.state.cursor_position += 1
        elif key == KeyCode.BACKSPACE.value:
            self.state.delete_char()
        elif key == KeyCode.DELETE.value and msvcrt.getch() == KeyCode.DELETE.value:
            self.state.forward_delete_char()
        elif len(key.decode(errors="ignore")) == 1:
            self.state.insert_char(key.decode(errors="ignore"))

        return super().handle_key(key)


def ask_input(
    question: str,
    description: str,
    placeholder: str = "",
    regex: Optional[str] = None,
    error_message: Optional[str] = None,
) -> str:
    """Display a text input prompt and return the user's input.

    Args:
        question: The question to display above the input
        description: Description text to show above the input
        placeholder: Placeholder text to show when input is empty
        regex: Optional regex pattern to validate input
        error_message: Custom error message for invalid input

    Returns:
        The user's input text

    Raises:
        KeyboardInterrupt: If user cancels with Esc or Ctrl+C
    """
    console = Console()
    config = InputConfig()
    state = TextInputState(config)
    handler = TextInputHandler(console, state, placeholder, regex, error_message)

    with CursorManager():
        try:
            while True:
                console.clear()
                handler.print_input(question, description)
                handler.update_cursor()

                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    result = handler.handle_key(key)
                    if result is not None:
                        return result
                else:
                    time.sleep(config.cpu_sleep_interval)
        finally:
            # Clean up the display
            sys.stdout.write("\033[4B")
            sys.stdout.write(" " * state.last_input_len)
            sys.stdout.write("\r")
            sys.stdout.flush()


class YesNoHandler(InputHandler[bool]):
    """Handler for yes/no input."""

    def __init__(self, console: Console):
        super().__init__(console)
        self.yes_selected = True

    def print_menu(self, question: str, description: str):
        """Print the yes/no menu."""
        menu = Text()
        if description:
            menu.append(f"{description}\n")

        helper = Text("Use arrow keys to navigate, Enter to select, or press Y/N.")
        helper.stylize("italic bright_black")
        menu.append(helper)
        menu.append("\n\n")

        yes_text = Text("-> Yes" if self.yes_selected else "   Yes")
        no_text = Text("   No" if self.yes_selected else "-> No")

        if self.yes_selected:
            yes_text.stylize("bold cyan")
        else:
            no_text.stylize("bold cyan")

        menu.append(yes_text)
        menu.append("\n")
        menu.append(no_text)

        self.console.print(Panel(menu, title=question, expand=False))

    def handle_key(self, key: bytes) -> Optional[bool]:
        """Handle yes/no input keys."""
        if key == KeyCode.ENTER.value:
            return self.yes_selected
        elif key == KeyCode.ARROW_PREFIX.value:
            arrow_key = msvcrt.getch()
            if arrow_key in (KeyCode.UP_ARROW.value, KeyCode.DOWN_ARROW.value):
                self.yes_selected = not self.yes_selected
        elif key.lower() == b"y":
            return True
        elif key.lower() == b"n":
            return False
        return super().handle_key(key)


def ask_yes_no(question: str, description: str = "") -> bool:
    """Display a yes/no prompt and return the user's choice.

    Args:
        question: The question to display above the prompt
        description: Optional description text to show above the choices

    Returns:
        True for Yes, False for No

    Raises:
        KeyboardInterrupt: If user cancels with Esc or Ctrl+C
    """
    console = Console()
    handler = YesNoHandler(console)

    while True:
        console.clear()
        handler.print_menu(question, description)

        if msvcrt.kbhit():
            key = msvcrt.getch()
            result = handler.handle_key(key)
            if result is not None:
                return result
