import asyncio

from textual.containers import Container
from textual.widgets import Label, ProgressBar

from src.lib.interface import interface


@interface("Progressbar Example")
async def example_2(container: Container):
    """
    Progress bar example.
    """
    progress_bar = ProgressBar(total=100, id="progress_bar")

    await container.mount(progress_bar)

    for _ in range(100):
        progress_bar.advance(1)
        await asyncio.sleep(0.1)

    await container.mount(Label("Progress bar complete!"))
