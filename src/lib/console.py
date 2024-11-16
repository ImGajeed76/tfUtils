"""
Terminal User Interface (TUI) input module providing interactive selection menus
and text input functionality with rich formatting.
"""

import re
from typing import Callable, Coroutine, Union

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.geometry import Spacing
from textual.screen import Screen
from textual.suggester import Suggester
from textual.validation import ValidationResult, Validator
from textual.widgets import Button, Footer, Input, Label


async def ask_input(
    container: Container,
    question: str,
    placeholder: str = "",
    password: bool = False,
    restrict: Union[str, None] = None,
    type: str = "text",
    max_length: int = 0,
    suggester: Union[Suggester, None] = None,
    button_text: str = "Enter",
    on_submit: Callable[[str], Union[Coroutine, None]] = None,
    regex: str = r"[\u0000-\uFFFF]*",
) -> None:
    """
    Ask the user for input with a regex validator.

    Example:
    ```python
    async def on_submit(vault_name: str) -> None:
        await container.mount(
            Label(f"Vault Name: {vault_name}", id="example_interface")
        )

    await ask_input(
        container,
        "Enter the name of the vault",
        placeholder="Vault Name",
        button_text="Create Vault",
        on_submit=on_submit,
        regex=r"Vault-\d{2}_[A-Za-z0-9]+$"
    )
    ```

    Args:
        container: The container to push the screen to
        question: The question to ask the user
        placeholder: The placeholder for the input field
        password: Whether the input should be a password
        restrict: The restrict pattern for character input
        type: The type of input field
        max_length: The maximum length of the input
        suggester: The suggester for the input field
        button_text: The text for the button
        on_submit: The callback for when the input is submitted
        regex: The regex pattern to validate the input
    """

    class RegexValidator(Validator):
        def validate(self, value: str) -> ValidationResult:
            if not re.match(regex, value):
                return self.failure(
                    f"Invalid input. Input must match the regex: {regex}"
                )
            return self.success()

    class InputScreen(Screen):
        valid_input: bool = False

        def compose(self) -> ComposeResult:
            input_label = Label(question)
            input_label.styles.margin = Spacing(1, 1, 1, 1)
            input_field = Input(
                placeholder=placeholder,
                password=password,
                restrict=restrict,
                type=type,
                max_length=max_length,
                suggester=suggester,
                validators=[RegexValidator()],
            )
            enter_button = Button(button_text, variant="primary")
            enter_button.styles.margin = Spacing(1, 1, 1, 1)

            error_label = Label("", id="error_label")
            error_label.styles.height = 0
            error_label.styles.margin = Spacing(0, 0, 0, 0)

            yield input_label
            yield input_field
            yield error_label
            yield enter_button
            yield Footer()

        @on(Input.Changed)
        def on_change(self, event: Input.Changed) -> None:
            self.valid_input = event.validation_result.is_valid

            enter_button = self.query_one(Button)
            error_label = self.query_one("#error_label", Label)

            if not self.valid_input:
                enter_button.disabled = True
                error_label.update(event.validation_result.failure_descriptions[0])
                error_label.styles.height = 1
                error_label.styles.margin = Spacing(1, 1, 1, 1)
                error_label.refresh()
            else:
                enter_button.disabled = False
                error_label.update("")
                error_label.styles.height = 0
                error_label.styles.margin = Spacing(0, 0, 0, 0)
                error_label.refresh()

        @on(Input.Submitted)
        def on_submit(self, event: Input.Submitted) -> None:
            if self.valid_input:
                self.dismiss(event.value)

        @on(Button.Pressed)
        def on_button(self) -> None:
            if self.valid_input:
                self.dismiss(self.query_one(Input).value)

    await container.app.push_screen(InputScreen(), callback=on_submit)


async def ask_yes_no(
    container: Container,
    question: str,
    on_submit: Callable[[bool], Union[None, Coroutine]],
    yes_text: str = "Yes",
    no_text: str = "No",
    default: bool = True,
) -> None:
    """
    Ask the user for a yes or no answer.

    Example:
    ```python
    async def on_submit(value: bool) -> None:
        print(f"You Pressed: {value}")

    await ask_yes_no(
        container,
        "Do you want to create a vault?",
        on_submit=on_submit,
    )
    ```

    Args:
        container: The container to display the prompt in.
        question: The question to ask the user.
        on_submit: The callback to call when the user submits the answer.
        yes_text: The text to display on the yes button.
        no_text: The text to display on the no button.
        default: The default answer to the question.
    """

    class InputScreen(Screen):
        BINDINGS = [
            Binding("y", "yes", "Yes"),
            Binding("n", "no", "No"),
        ]

        def compose(self) -> ComposeResult:
            input_label = Label(question)
            input_label.styles.margin = Spacing(1, 1, 1, 1)

            yes_button = Button(yes_text, id="yes_btn", variant="success")
            yes_button.styles.margin = Spacing(1, 1, 1, 1)
            no_button = Button(no_text, id="no_btn", variant="error")
            no_button.styles.margin = Spacing(1, 1, 1, 1)

            yield input_label
            yield Horizontal(yes_button, no_button)
            yield Footer()

            if default:
                yes_button.focus()
            else:
                no_button.focus()

        @on(Button.Pressed)
        def on_button(self, event: Button.Pressed) -> None:
            self.dismiss(event.button.id == "yes_btn")

        def action_yes(self) -> None:
            self.dismiss(True)

        def action_no(self) -> None:
            self.dismiss(False)

    await container.app.push_screen(InputScreen(), callback=on_submit)
