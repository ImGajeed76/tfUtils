import sys
from typing import Callable, Iterable

from textual import on
from textual.app import App, ComposeResult, SystemCommand
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Header, Label, ListItem, ListView, Static


class InterfaceTree:
    children = []
    path = ""

    def __init__(
        self,
        name: str,
        description: str = "",
        id: str = "",
        is_root: bool = False,
        on_select: Callable[[Static], None] = None,
        app: "InterfaceViewer" = None,
    ):
        self.name = name
        self.description = description or name
        self.children = []
        self.is_root = is_root
        self.on_select = on_select
        self.id = id
        if id == "":
            self.id = "".join(
                [c if c.isalnum() else "_" for c in name.lower().replace(" ", "_")]
            )
        self.app = app

    def add_child(self, child: "InterfaceTree"):
        self.children.append(child)

    def set_app(self, app: App):
        self.app = app
        for child in self.children:
            child.set_app(app)

    def generate_path(self, path: str = ""):
        if path == "":
            path = self.id
        else:
            path = f"{path}/{self.id}"
        self.path = path
        for child in self.children:
            child.generate_path(path)

    def __on_select_wrapper(self):
        if self.app is not None and self.on_select is not None:
            try:
                self.app.query_one("#interface_viewer").remove()
            except Exception:
                pass

            interface = None

            try:
                interface = self.app.query_one("#interface")
            except Exception:
                pass

            if interface is not None:
                interface.query_children("*").remove()
            else:
                interface = Static(id="interface")

            interface.refresh()

            self.app.path = self.path
            self.app.update_path()
            self.app.mount(interface)
            self.on_select(interface)

    def __str__(self):
        return f"{self.name} ({len(self.children)} children)"

    def __repr__(self):
        return f"InterfaceTree({self.name!r}, {len(self.children)!r})"

    def get_textual(self, path: str = "") -> Iterable[ListItem]:
        path_parts = path.split("/")
        if path_parts[0] == self.id:
            path_parts = path_parts[1:]
            if len(path_parts) == 0:
                if not self.is_root:
                    yield ListItem(
                        Label("← Back"), name="Go one section back", id="back"
                    )

                if len(self.children) == 0:
                    self.__on_select_wrapper()
                else:
                    for child in self.children:
                        if child.on_select is not None or len(child.children) > 0:
                            yield ListItem(
                                Label(child.name), name=child.description, id=child.id
                            )
            else:
                for child in self.children:
                    if child.id == path_parts[0]:
                        yield from child.get_textual("/".join(path_parts))
                        break

    def register_system_commands(self) -> Iterable[SystemCommand]:
        if len(self.children) == 0:
            yield SystemCommand(self.name, self.description, self.__on_select_wrapper)

        for child in self.children:
            yield from child.register_system_commands()


def example_function(container: Static):
    container.mount(Label("Hello, World!"))


example_tree = InterfaceTree("root", is_root=True)
sub_one = InterfaceTree(
    "Sub One", "This is the first sub tree. \nIt has three children."
)
sub_two = InterfaceTree("Sub Two")
sub_three = InterfaceTree("Sub Three")
sub_one.add_child(InterfaceTree("Sub One A", on_select=example_function))
sub_one.add_child(InterfaceTree("Sub One B", on_select=example_function))
sub_one.add_child(InterfaceTree("Sub One C", on_select=example_function))
sub_two.add_child(InterfaceTree("Sub Two A", on_select=example_function))
sub_two.add_child(InterfaceTree("Sub Two B", on_select=example_function))
sub_two.add_child(InterfaceTree("Sub Two C", on_select=example_function))
sub_three.add_child(InterfaceTree("Sub Three A", on_select=example_function))
sub_three.add_child(InterfaceTree("Sub Three B", on_select=example_function))
sub_three.add_child(InterfaceTree("Sub Three C", on_select=example_function))
example_tree.add_child(sub_one)
example_tree.add_child(sub_two)
example_tree.add_child(sub_three)


class InterfaceViewer(App):
    TITLE = "TF Utils"
    CSS_PATH = "src/tcss/interface_viewer.tcss"

    path = "root"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(id="path")

    async def show_main(self):
        try:
            await self.query_one("#interface", expect_type=Static).remove()
        except Exception:
            pass

        interface_viewer = None

        try:
            interface_viewer = self.query_one(
                "#interface_viewer", expect_type=Horizontal
            )
        except Exception:
            pass

        if interface_viewer is None:
            await self.mount(
                Horizontal(
                    ListView(
                        id="interface_tree",
                        initial_index=0,
                    ),
                    Label("Hello, World!", id="option_info"),
                    id="interface_viewer",
                )
            )

        self.path = "root"
        await self.update_selector()

    @on(ListView.Highlighted)
    def update_label(self, event: ListView.Highlighted):
        if event.item is None:
            return
        self.query_one("#option_info", expect_type=Label).update(str(event.item.name))

    @on(ListView.Selected)
    async def select_option(self, event: ListView.Selected):
        if event.item is None or event.item.name is None:
            return

        if event.item.id == "back":
            self.path = "/".join(self.path.split("/")[:-1])
        else:
            self.path = f"{self.path}/{event.item.id}"

        await self.update_selector()

    async def update_selector(self):
        self.update_path()
        interface_tree = self.query_one("#interface_tree", expect_type=ListView)
        await interface_tree.clear()
        await interface_tree.extend(example_tree.get_textual(self.path))
        interface_tree.index = 0
        interface_tree.refresh()

    def update_path(self):
        self.query_one("#path", expect_type=Label).update(self.path)

    async def on_mount(self) -> None:
        example_tree.set_app(self)
        example_tree.generate_path()
        await self.show_main()

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        yield SystemCommand("Home", "Return to the main menu", self.show_main)
        yield from example_tree.register_system_commands()


def main():
    app = InterfaceViewer()
    app.run()
    sys.exit(app.return_code or 0)


if __name__ == "__main__":
    main()
