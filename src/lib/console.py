import msvcrt
import re
import sys
import time
from itertools import count

from rich.console import Console
from rich.panel import Panel
from rich.text import Text


def ask_select(prompt: str, choices: list[str], default: int = 0) -> int:
    console = Console()
    selected = default if 0 <= default < len(choices) else 0

    def print_menu():
        menu = [
            "[italic]Use arrow keys to navigate, Enter to select, or press the number key.[/italic]",
            ""
        ]
        for i, choice in enumerate(choices):
            if i == selected:
                menu.append(f"[bold cyan]-> {i + 1}. {choice}[/bold cyan]")
            else:
                menu.append(f"   {i + 1}. {choice}")
        panel = Panel("\n".join(menu), title=prompt, expand=False)
        console.print(panel)

    while True:
        console.clear()
        print_menu()

        key = msvcrt.getch()
        if key == b'\r':  # Enter key
            return selected
        elif key == b'\xe0':  # Arrow keys
            key = msvcrt.getch()
            if key == b'H' and selected > 0:  # Up arrow
                selected -= 1
            elif key == b'P' and selected < len(choices) - 1:  # Down arrow
                selected += 1
        elif key in [b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9']:
            index = int(key.decode()) - 1
            if 0 <= index < len(choices):
                selected = index
                console.clear()
                print_menu()
                return selected
        elif key == b'\x1b':  # Esc key
            raise KeyboardInterrupt
        elif key == b'\x03':  # Ctrl+C
            raise KeyboardInterrupt


def hide_cursor():
    sys.stdout.write('\033[?25l')
    sys.stdout.flush()

def show_cursor():
    sys.stdout.write('\033[?25h')
    sys.stdout.flush()


def ask_input(question: str, description: str, placeholder: str = "", regex: str = None,
              error_message: str = None) -> str:
    console = Console()
    user_input = ""
    cursor_position = 0
    blink_state = True
    last_blink = time.time()
    error = ""
    last_input_len = 0
    max_length = 36

    def print_full_input():
        input_text = Text()
        if user_input:
            input_text.append(user_input)
        else:
            input_text.append(f"[bright_black]{placeholder}[/bright_black]")

        content = f"{description}\n\n{input_text}\n\n[blue]Press Enter to submit, Esc to cancel[/blue]"
        if error:
            content += f"\n\n[bold red]{error}[/bold red]"

        panel = Panel(content, title=f"[green]{question}[/green]", expand=False)
        console.clear()
        console.print(panel)

    def update_cursor(force_blink_state=None, move_cursor=False):
        nonlocal blink_state, last_blink, last_input_len
        current_time = time.time()
        if force_blink_state is not None:
            blink_state = force_blink_state
        elif current_time - last_blink > 0.5:
            blink_state = not blink_state
            last_blink = current_time

        #sys.stdout.write(f"\033[{console.height}A")  # Move to top of console
        #sys.stdout.write(f"\033[3B\033[2C")  # Move down 3 lines and right 2 characters

        # move up 4 lines
        up_cnt = 4
        if error:
            up_cnt += 2
        if error_message and error:
            up_cnt += error_message.count("\n")
        if move_cursor:
            sys.stdout.write(f"\033[{up_cnt}A")
            # move right 2 characters
        sys.stdout.write(f"\r\033[2C")
        # Clear the line
        sys.stdout.write(" " * last_input_len)
        # Move back to the beginning of the line + 2 characters
        sys.stdout.write(f"\r\033[2C")

        sys.stdout.write(user_input[:cursor_position])
        if blink_state:
            sys.stdout.write("█")
        else:
            if len(user_input) == 0:
                # print first character of placeholder in bright black
                # use console color codes for color
                sys.stdout.write(f"\033[90m{placeholder[0]}\033[97m")

            else:
                sys.stdout.write(user_input[cursor_position] if cursor_position < len(user_input) else " ")
        sys.stdout.write(user_input[cursor_position + 1:])

        sys.stdout.flush()

        # Save the length of the input for clearing the line
        last_input_len = len(user_input) + 1

    hide_cursor()
    try:
        print_full_input()
        update_cursor(move_cursor=True)
        while True:
            update_cursor()

            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b'\r':  # Enter key
                    if user_input:
                        if regex is None or re.match(regex, user_input):
                            return user_input
                        else:
                            error = error_message or "Input does not match the required format. Please try again."
                            print_full_input()
                            update_cursor(move_cursor=True)
                    else:
                        return placeholder

                elif key == b'\xe0':  # Arrow keys
                    key = msvcrt.getch()
                    if key == b'K' and cursor_position > 0:  # Left arrow
                        cursor_position -= 1
                    elif key == b'M' and cursor_position < len(user_input):  # Right arrow
                        cursor_position += 1
                    update_cursor(force_blink_state=True)
                elif key == b'\x08':  # Backspace
                    if cursor_position > 0:
                        user_input = user_input[:cursor_position - 1] + user_input[cursor_position:]
                        cursor_position -= 1
                        update_cursor(force_blink_state=True)

                        if len(user_input) == 0 or len(user_input) == 1 or error:
                            error = ""
                            print_full_input()
                            update_cursor(move_cursor=True)

                        if len(user_input) >= max_length:
                            print_full_input()
                            update_cursor(move_cursor=True)
                elif key == b'\xe0':  # Delete (captured as two keystrokes)
                    if msvcrt.getch() == b'S' and cursor_position < len(user_input):
                        user_input = user_input[:cursor_position] + user_input[cursor_position + 1:]
                        update_cursor(force_blink_state=True)

                        if len(user_input) == 0 or len(user_input) == 1 or error:
                            error = ""
                            print_full_input()
                            update_cursor(move_cursor=True)

                        if len(user_input) >= max_length:
                            print_full_input()
                            update_cursor(move_cursor=True)
                elif key == b'\x1b':  # Esc key
                    raise KeyboardInterrupt
                elif key == b'\x03':  # Ctrl+C
                    raise KeyboardInterrupt
                elif len(key.decode(errors='ignore')) == 1:  # Printable characters
                    user_input = user_input[:cursor_position] + key.decode(errors='ignore') + user_input[
                                                                                              cursor_position:]
                    cursor_position += 1
                    update_cursor(force_blink_state=True)

                    if len(user_input) == 0 or len(user_input) == 1 or error:
                        error = ""
                        print_full_input()
                        update_cursor(move_cursor=True)

                    if len(user_input) >= max_length:
                        print_full_input()
                        update_cursor(move_cursor=True)
            else:
                time.sleep(0.01)  # Small delay to reduce CPU usage
    finally:
        # move down 3 lines
        sys.stdout.write(f"\033[4B")
        # Clear the line
        sys.stdout.write(" " * last_input_len)
        # Move back to the beginning of the line
        sys.stdout.write("\r")
        sys.stdout.flush()

        show_cursor()


def ask_yes_no(question: str, description: str = "") -> bool:
    console = Console()
    yes_selected = True

    def print_menu():
        menu = Text()
        menu.append(description)
        if description:
            menu.append("\n")

        helper = Text("Use arrow keys to navigate, Enter to select, or press Y/N.")
        helper.stylize("italic")
        helper.stylize("bright_black")
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
        console.print(panel)

    while True:
        console.clear()
        print_menu()

        key = msvcrt.getch()
        if key == b'\r':  # Enter key
            return yes_selected
        elif key == b'\xe0':  # Arrow keys
            key = msvcrt.getch()
            if key in (b'H', b'P'):  # Up or Down arrow
                yes_selected = not yes_selected
        elif key.lower() == b'y':
            yes_selected = True
            console.clear()
            print_menu()
            return True
        elif key.lower() == b'n':
            yes_selected = False
            console.clear()
            print_menu()
            return False
        elif key == b'\x1b':  # Esc key
            raise KeyboardInterrupt
        elif key == b'\x03':  # Ctrl+C
            raise KeyboardInterrupt
