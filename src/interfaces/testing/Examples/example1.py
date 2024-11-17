from textual.containers import Container
from textual.widgets import Label

from src.lib.console import ask_input
from src.lib.interface import interface


@interface("Example 1")
async def example_callback(container: Container):
    """
    This is the description of the example interface callback.

    It asks the user for their name.
    """

    name = await ask_input(
        container,
        "What is your name?",
    )

    await container.mount(Label(f"Hello, {name}!"))
