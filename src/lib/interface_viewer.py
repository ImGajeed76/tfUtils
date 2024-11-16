import sys
from typing import Callable, Coroutine, Iterable, List, Union

from textual import on
from textual.app import App, ComposeResult, SystemCommand
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, ListItem, ListView


class InterfacePath:
    original_path: str
    path: str

    def __init__(self, original_path: str = ""):
        self.original_path = original_path
        self._set_path(original_path)

    def _set_path(self, path: str):
        self.path = self.sanitize_path(path)

    @staticmethod
    def sanitize_path(path: str):
        path = path.lower()
        path = path.replace("\\\\", "/")
        path = path.replace("\\", "/")
        path = path.replace("-", "_")
        path = path.replace("/", "-")
        path = "".join([c if c.isalnum() or c == "-" else "_" for c in path])
        return path

    def __str__(self):
        return self.path

    def __repr__(self):
        return f"InterfacePath: {self.path} ({self.original_path})"

    def __eq__(self, other):
        return self.path == other.path

    def __truediv__(self, other):
        return InterfacePath(f"{self.original_path}/{other.original_path}")

    def parent(self):
        return InterfacePath("/".join(self.original_path.split("/")[:-1]))


class InterfaceReference:
    path: InterfacePath

    name: str
    description: str
    call_back: Callable[[Container], Coroutine]

    active: bool = True

    def __init__(
        self,
        path: Union[InterfacePath, str],
        name: str,
        description: str,
        call_back: Callable[[Container], Coroutine] = None,
        active: bool = True,
    ):
        if isinstance(path, str):
            path = InterfacePath(path)
        self.path = path
        self.name = name
        self.description = description
        self.call_back = call_back
        self.active = active

    def __str__(self):
        return (
            f"InterfaceReference: "
            f"{self.path.parent()} -> {self.name} -> {self.description}"
        )

    def __repr__(self):
        return f"""InterfaceReference:
- path: {self.path}
- parent_path: {self.path.parent()}
- name: {self.name}
- description: {self.description}
- call_back: {self.call_back}
        """


class InterfaceViewer(App):
    path = InterfacePath("root")

    CSS_PATH = "../tcss/interface_viewer.tcss"

    BINDINGS = [
        ("^c", "quit", "quit"),
    ]

    def __init__(self, title: str, references: List[InterfaceReference]):
        self.TITLE = title
        super().__init__()
        self.references = references

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(str(self.path), id="path")
        yield Container(id="view_port")
        yield Footer()

    async def mount_reference_viewer(self):
        self.path = InterfacePath("root")
        await self._update_path()
        view_port = self.query_one("#view_port", Container)
        await view_port.query_children().remove()
        await view_port.mount(
            Horizontal(
                ListView(id="reference_list", initial_index=0),
                Label("Select an interface to view info", id="reference_info"),
                id="reference_viewer",
            )
        )

        await self._update_reference_viewer()

    async def mount_reference(self):
        view_port = self.query_one("#view_port", Container)
        await view_port.query_children().remove()
        await view_port.mount(Container(id="interface"))

    async def _update_reference_viewer(self):
        await self._update_path()

        reference_list = self.query_one("#reference_list", ListView)
        await reference_list.clear()
        if str(self.path) != "root":
            await reference_list.mount(
                ListItem(
                    Label("← Back"), name="Go back to the previous menu.", id="back"
                )
            )
        for reference in self.references:
            if reference.path.parent() == self.path:
                await reference_list.mount(
                    ListItem(
                        Label(reference.name),
                        name=reference.description,
                        id=str(reference.path),
                        disabled=not reference.active,
                    )
                )

        reference_list.index = 0
        reference_list.refresh()
        reference_list.focus()

    async def _update_path(self):
        path_label = self.query_one("#path", Label)
        path_label.update(str(self.path))

    @on(ListView.Highlighted)
    def update_info(self, event: ListView.Highlighted):
        if event.item is None:
            return
        self.query_one("#reference_info", expect_type=Label).update(
            str(event.item.name)
        )

    @on(ListView.Selected)
    async def select_reference(self, event: ListView.Selected):
        if event.item is None or event.item.name is None:
            return

        if event.item.id == "back":
            self.path = self.path.parent()
        else:
            reference = self._get_reference_by_id(event.item.id)
            if reference is None:
                return

            self.path = reference.path

            if reference.call_back is not None:
                await self._update_path()
                await self._call_reference_callback(reference)
                return

        await self._update_reference_viewer()

    async def _call_reference_callback(self, reference: InterfaceReference):
        await self.mount_reference()
        interface_container = self.query_one("#interface", Container)
        await reference.call_back(interface_container)

    async def _call_reference_callback_by_id(self, reference_id: str):
        reference = self._get_reference_by_id(reference_id)
        if reference is not None:
            await self._call_reference_callback(reference)

    def _get_reference_by_id(
        self, reference_id: str
    ) -> Union[InterfaceReference, None]:
        for reference in self.references:
            if str(reference.path) == reference_id:
                return reference
        return None

    async def on_mount(self):
        await self.mount_reference_viewer()

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        yield SystemCommand(
            "Home", "Return to the main menu", self.mount_reference_viewer
        )

        for reference in self.references:
            if reference.call_back is not None:
                yield SystemCommand(
                    reference.path.original_path,
                    reference.description,
                    lambda ref=reference: self._call_reference_callback_by_id(
                        str(ref.path)
                    ),
                )


def main():
    async def example_callback(container: Container):
        await container.mount(
            Label("This is an example interface", id="example_interface")
        )

    async def example_callback2(container: Container):
        await container.mount(
            Label("This is another example interface", id="example_interface2")
        )

    example_references = [
        InterfaceReference("root", "interface", "Root interface"),
        InterfaceReference("root/interface1", "example1", "Example interface 1"),
        InterfaceReference(
            "root/interface1/example1",
            "function1",
            "Example function 1",
            example_callback,
        ),
        InterfaceReference(
            "root/interface1/example2", "function2", "Example function 2", active=False
        ),
        InterfaceReference(
            "root/interface1/example3", "function3", "Example function 3"
        ),
        InterfaceReference("root/interface2", "example2", "Example interface 2"),
        InterfaceReference(
            "root/interface2/example1", "function1", "Example function 1"
        ),
        InterfaceReference(
            "root/interface2/example2",
            "function2",
            "Example function 2",
            example_callback2,
        ),
        InterfaceReference(
            "root/interface2/example3", "function3", "Example function 3", active=False
        ),
    ]

    app = InterfaceViewer("Interface Viewer", example_references)
    app.run()
    sys.exit(app.return_code or 0)


if __name__ == "__main__":
    main()
