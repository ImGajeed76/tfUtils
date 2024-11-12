"""
Terminal User Interface (TUI) input module providing interactive selection menus
and text input functionality with rich formatting.
"""

import msvcrt
import re
import sys
import time
from dataclasses import dataclass
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.text import Text


@dataclass
class CursorState:
    """Manages cursor state for text input."""

    position: int = 0
    blink_state: bool = True
    last_blink: float = time.time()
    last_input_len: int = 0


class CursorManager:
    """Handles cursor visibility in the terminal."""

    @staticmethod
    def hide():
        """Hide the terminal cursor."""
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

    @staticmethod
    def show():
        """Show the terminal cursor."""
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()


class MenuRenderer:
    """Handles rendering of selection menus."""

    def __init__(self, console: Console):
        self.console = console

    def render_selection_menu(
        self, prompt: str, choices: list[str], selected: int
    ) -> None:
        """Render a selection menu with the current choice highlighted."""
        menu = [
            "[italic]"
            "Use arrow keys to navigate, "
            "Enter to select, "
            "or press the number key."
            "[/italic]",
            "",
        ]

        for i, choice in enumerate(choices):
            if i == selected:
                menu.append(f"[bold cyan]-> {i + 1}. {choice}[/bold cyan]")
            else:
                menu.append(f"   {i + 1}. {choice}")

        panel = Panel("\n".join(menu), title=prompt, expand=False)
        self.console.print(panel)

    def render_yes_no_menu(
        self, question: str, description: str, yes_selected: bool
    ) -> None:
        """Render a Yes/No selection menu."""
        menu = Text()
        menu.append(description)
        if description:
            menu.append("\n")

        helper = Text("Use arrow keys to navigate, Enter to select, or press Y/N.")
        helper.stylize("italic bright_black")
        menu.append(helper)
        menu.append("\n\n")

        yes_text = Text("-> Yes" if yes_selected else "   Yes")
        no_text = Text("   No" if yes_selected else "-> No")

        if yes_selected:
            yes_text.stylize("bold cyan")
        else:
            no_text.stylize("bold cyan")

        menu.append(yes_text)
        menu.append("\n")
        menu.append(no_text)

        panel = Panel(menu, title=question, expand=False)
        self.console.print(panel)


class InputHandler:
    """Handles text input with cursor management and validation."""

    def __init__(self, console: Console):
        self.console = console
        self.max_length = 36

    def render_input_panel(
        self,
        question: str,
        description: str,
        user_input: str,
        placeholder: str,
        error: str,
    ) -> None:
        """Render the input panel with current state."""
        input_text = Text()
        if user_input:
            input_text.append(user_input)
        else:
            input_text.append(f"[bright_black]{placeholder}[/bright_black]")

        content = (
            f"{description}\n\n{input_text}\n\n"
            f"[blue]Press Enter to submit, Esc to cancel[/blue]"
        )
        if error:
            content += f"\n\n[bold red]{error}[/bold red]"

        panel = Panel(content, title=f"[green]{question}[/green]", expand=False)
        self.console.clear()
        self.console.print(panel)

    def update_cursor_position(
        self,
        user_input: str,
        cursor: CursorState,
        placeholder: str,
        error: str,
        force_blink_state: Optional[bool] = None,
        move_cursor: bool = False,
    ) -> None:
        """Update the cursor position and state."""
        current_time = time.time()
        if force_blink_state is not None:
            cursor.blink_state = force_blink_state
        elif current_time - cursor.last_blink > 0.5:
            cursor.blink_state = not cursor.blink_state
            cursor.last_blink = current_time

        up_cnt = 4 + (2 if error else 0)
        if error:
            up_cnt += error.count("\n")

        if move_cursor:
            sys.stdout.write(f"\033[{up_cnt}A")
        sys.stdout.write("\r\033[2C")
        sys.stdout.write(" " * cursor.last_input_len)
        sys.stdout.write("\r\033[2C")

        sys.stdout.write(user_input[: cursor.position])
        if cursor.blink_state:
            sys.stdout.write("█")
        else:
            if not user_input and placeholder:
                sys.stdout.write(f"\033[90m{placeholder[0]}\033[97m")
            else:
                sys.stdout.write(
                    user_input[cursor.position]
                    if cursor.position < len(user_input)
                    else " "
                )
        sys.stdout.write(user_input[cursor.position + 1 :])

        sys.stdout.flush()
        cursor.last_input_len = len(user_input) + 1


def ask_select(prompt: str, choices: list[str], default: int = 0) -> int:
    """Display an interactive selection menu."""
    console = Console()
    renderer = MenuRenderer(console)
    selected = default if 0 <= default < len(choices) else 0

    while True:
        console.clear()
        renderer.render_selection_menu(prompt, choices, selected)

        key = msvcrt.getch()
        if key == b"\r":  # Enter
            return selected
        elif key == b"\xe0":  # Arrow keys
            key = msvcrt.getch()
            if key == b"H" and selected > 0:  # Up
                selected -= 1
            elif key == b"P" and selected < len(choices) - 1:  # Down
                selected += 1
        elif key in [b"1", b"2", b"3", b"4", b"5", b"6", b"7", b"8", b"9"]:
            index = int(key.decode()) - 1
            if 0 <= index < len(choices):
                selected = index
                console.clear()
                renderer.render_selection_menu(prompt, choices, selected)
                return selected
        elif key in (b"\x1b", b"\x03"):  # Esc or Ctrl+C
            raise KeyboardInterrupt


def ask_input(
    question: str,
    description: str,
    placeholder: str = "",
    regex: str = None,
    error_message: str = None,
) -> str:
    """Display an interactive text input prompt with validation."""
    console = Console()
    handler = InputHandler(console)
    user_input = ""
    cursor = CursorState()
    error = ""

    CursorManager.hide()
    try:
        handler.render_input_panel(
            question, description, user_input, placeholder, error
        )
        handler.update_cursor_position(
            user_input, cursor, placeholder, error, move_cursor=True
        )

        while True:
            handler.update_cursor_position(user_input, cursor, placeholder, error)

            if msvcrt.kbhit():
                key = msvcrt.getch()

                if key == b"\r":  # Enter
                    if user_input:
                        if regex is None or re.match(regex, user_input):
                            return user_input
                        error = (
                            error_message
                            or "Input does not match the required format. "
                            "Please try again."
                        )
                        handler.render_input_panel(
                            question, description, user_input, placeholder, error
                        )
                        handler.update_cursor_position(
                            user_input, cursor, placeholder, error, move_cursor=True
                        )
                    else:
                        return placeholder

                elif key == b"\xe0":  # Arrow keys
                    key = msvcrt.getch()
                    if key == b"K" and cursor.position > 0:  # Left
                        cursor.position -= 1
                    elif key == b"M" and cursor.position < len(user_input):  # Right
                        cursor.position += 1
                    handler.update_cursor_position(
                        user_input, cursor, placeholder, error, force_blink_state=True
                    )

                elif key == b"\x08":  # Backspace
                    if cursor.position > 0:
                        user_input = (
                            user_input[: cursor.position - 1]
                            + user_input[cursor.position :]
                        )
                        cursor.position -= 1
                        handler.update_cursor_position(
                            user_input,
                            cursor,
                            placeholder,
                            error,
                            force_blink_state=True,
                        )

                        if len(user_input) <= 1 or error:
                            error = ""
                            handler.render_input_panel(
                                question, description, user_input, placeholder, error
                            )
                            handler.update_cursor_position(
                                user_input, cursor, placeholder, error, move_cursor=True
                            )

                        if len(user_input) >= handler.max_length:
                            handler.render_input_panel(
                                question, description, user_input, placeholder, error
                            )
                            handler.update_cursor_position(
                                user_input, cursor, placeholder, error, move_cursor=True
                            )

                elif key == b"\xe0" and msvcrt.getch() == b"S":  # Delete
                    if cursor.position < len(user_input):
                        user_input = (
                            user_input[: cursor.position]
                            + user_input[cursor.position + 1 :]
                        )
                        handler.update_cursor_position(
                            user_input,
                            cursor,
                            placeholder,
                            error,
                            force_blink_state=True,
                        )

                        if len(user_input) <= 1 or error:
                            error = ""
                            handler.render_input_panel(
                                question, description, user_input, placeholder, error
                            )
                            handler.update_cursor_position(
                                user_input, cursor, placeholder, error, move_cursor=True
                            )

                        if len(user_input) >= handler.max_length:
                            handler.render_input_panel(
                                question, description, user_input, placeholder, error
                            )
                            handler.update_cursor_position(
                                user_input, cursor, placeholder, error, move_cursor=True
                            )

                elif key in (b"\x1b", b"\x03"):  # Esc or Ctrl+C
                    raise KeyboardInterrupt

                elif len(key.decode(errors="ignore")) == 1:  # Printable characters
                    user_input = (
                        user_input[: cursor.position]
                        + key.decode(errors="ignore")
                        + user_input[cursor.position :]
                    )
                    cursor.position += 1
                    handler.update_cursor_position(
                        user_input, cursor, placeholder, error, force_blink_state=True
                    )

                    if len(user_input) <= 1 or error:
                        error = ""
                        handler.render_input_panel(
                            question, description, user_input, placeholder, error
                        )
                        handler.update_cursor_position(
                            user_input, cursor, placeholder, error, move_cursor=True
                        )

                    if len(user_input) >= handler.max_length:
                        handler.render_input_panel(
                            question, description, user_input, placeholder, error
                        )
                        handler.update_cursor_position(
                            user_input, cursor, placeholder, error, move_cursor=True
                        )
            else:
                time.sleep(0.01)  # Reduce CPU usage
    finally:
        sys.stdout.write("\033[4B")  # Move down 4 lines
        sys.stdout.write(" " * cursor.last_input_len)  # Clear the line
        sys.stdout.write("\r")  # Move to line start
        sys.stdout.flush()
        CursorManager.show()


def ask_yes_no(question: str, description: str = "") -> bool:
    """Display an interactive Yes/No selection menu."""
    console = Console()
    renderer = MenuRenderer(console)
    yes_selected = True

    while True:
        console.clear()
        renderer.render_yes_no_menu(question, description, yes_selected)

        key = msvcrt.getch()
        if key == b"\r":  # Enter
            return yes_selected
        elif key == b"\xe0":  # Arrow keys
            key = msvcrt.getch()
            if key in (b"H", b"P"):  # Up or Down
                yes_selected = not yes_selected
        elif key.lower() == b"y":
            yes_selected = True
            console.clear()
            renderer.render_yes_no_menu(question, description, yes_selected)
            return True
        elif key.lower() == b"n":
            yes_selected = False
            console.clear()
            renderer.render_yes_no_menu(question, description, yes_selected)
            return False
        elif key in (b"\x1b", b"\x03"):  # Esc or Ctrl+C
            raise KeyboardInterrupt
