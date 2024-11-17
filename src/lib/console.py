"""
Textual Wrappers for common console prompts.
"""

import re
from typing import Union

from textual import events, on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.geometry import Spacing
from textual.screen import Screen
from textual.suggester import Suggester
from textual.validation import ValidationResult, Validator
from textual.widgets import Button, Footer, Input, Label, ListItem, ListView


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
    regex: str = r"[\u0000-\uFFFF]*",
) -> str:
    """
    Ask the user for input with a regex validator.

    Example:
    ```python
    name = await ask_input(
        container,
        "Enter the name of the vault",
        placeholder="Vault Name",
        button_text="Create Vault",
        regex=r"Vault-\d{2}_[A-Za-z0-9]+$"
    )

    await container.mount(Label(f"Vault Name: {name}"))
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

    return await container.app.push_screen_wait(InputScreen())


async def ask_yes_no(
    container: Container,
    question: str,
    yes_text: str = "Yes",
    no_text: str = "No",
    default: bool = True,
) -> None:
    """
    Ask the user for a yes or no answer.

    Example:
    ```python
    answer = await ask_yes_no(
        container,
        "Do you want to create a vault?"
    )

    await container.mount(Label(f"Answer: {'Yes' if answer else 'No'}"))
    ```

    Args:
        container: The container to display the prompt in.
        question: The question to ask the user.
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

    return await container.app.push_screen_wait(InputScreen())


async def ask_select(
    container: Container,
    question: str,
    options: list[str],
) -> str:
    """
    Ask the user to select an option from a list.

    Example:
    ```python
    option = await ask_select(
        container,
        "Select a color",
        ["Red", "Green", "Blue"]
    )

    await container.mount(Label(f"Selected: {option}"))
    ```

    Args:
        container: The container to display the prompt in.
        question: The question to ask the user.
        options: The list of options to select from.
    """

    class InputScreen(Screen):
        list_view: ListView

        def compose(self) -> ComposeResult:
            input_label = Label(question)
            input_label.styles.margin = Spacing(1, 1, 1, 1)

            self.list_view = ListView()

            yield input_label
            yield self.list_view
            yield Footer()

        def _on_mount(self, event: events.Mount) -> None:
            for option in options:
                self.list_view.append(ListItem(Label(option), name=option))
            self.list_view.index = 0
            self.list_view.refresh()
            self.list_view.focus()

        @on(ListView.Selected)
        def on_select(self, event: ListView.Selected) -> None:
            self.dismiss(event.item.name)

    return await container.app.push_screen_wait(InputScreen())
