from textual.containers import Container
from textual.widgets import Label

from src.lib.console import ask_input, ask_yes_no
from src.lib.interface import interface


@interface("Example 1")
async def example_callback(container: Container):
    """
    This is the description of the example interface callback.

    It asks the user for their name and then asks if they are ready to continue.
    """

    def on_yes_no_submit(value2: bool) -> None:
        if value2:
            container.mount(Label("You said yes!"))
        else:
            container.mount(Label("You said no!"))

    async def on_name_submit(value: str) -> None:

        await ask_yes_no(
            container,
            f"Hello, {value}! Are you ready to continue?",
            on_submit=on_yes_no_submit,
        )

    await ask_input(
        container,
        "What is your name?",
        on_submit=on_name_submit,
    )
