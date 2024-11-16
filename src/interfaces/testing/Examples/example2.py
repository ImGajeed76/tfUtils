from textual.containers import Container
from textual.widgets import Label

from src.lib.interface import interface


@interface("Example 2")
async def example_2(container: Container):
    """
    This example has a code snippet in the description.

    ```python
    if __name__ == "__main__":
        print("Hello, World!")
    ```

    """
    await container.mount(Label("This is example 2!"))
