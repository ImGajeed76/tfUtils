title: TF Utils

---

#description

A user-friendly tool that helps TFBern students manage their projects more efficiently. Perfect for both beginners and advanced users, TF Utils streamlines project workflows with its intuitive interface and powerful features.

#main

# TF Utils: Making Project Setup Less Annoying

## The Idea: What It Is and Why I Built It

At its core, TF Utils is a little command-line tool with a friendly text-based interface (TUI) that helps automate some of the tedious parts of setting up projects. Specifically, it's designed for fellow apprentices in the Electronics Technician (Elektroniker) program at TFBern.

Honestly, the whole idea started because I was getting really frustrated myself. As an apprentice here, I also enjoy coding, and the constant cycle of copying project templates, carefully renaming everything, trying to keep track of versions, and dealing with inconsistencies across projects felt super inefficient. I thought, "There has to be a better way," so I decided to build one. My goal was basically to scratch my own itch and hopefully make things a bit easier for others in the program too.

## The Journey: From Simple Script to TUI Tool

It didn't start as anything fancy. My first attempt was just a small Python script to make the standard uVision templates we use work nicely with CLion, which is the IDE I prefer. But I quickly realized that just patching templates wasn't enough. I wanted to handle more tasks, and a single script was going to get messy fast.

That led me to think about a more organized approach. I started building a system where I could define different tasks or "commands" in separate files. The main program would automatically find these commands and show them in a simple console menu. This worked okay for a while, but managing the user interaction in the console got complicated as I added more features.

That's when I discovered **Textual**, a Python library for building TUIs. It was a game-changer! Suddenly, I didn't have to wrestle with printing menus, handling user input, or clearing the screen manually. Textual provided cool features like pop-up modals and even mouse support, letting me focus on the actual _logic_ of the commands.

Adding new commands became much cleaner. For example, you can just create a new Python file (like `hello.py`) in the `interfaces` folder, write a function, and add a simple `@interface` decorator:

```py
# Example: interfaces/hello.py
from textual.containers import Container
from src.lib.interface import interface # My custom decorator
from src.lib.utils import console

@interface("My First Interface") # This makes it show up in the TUI
async def hello_world(container: Container):
    """This is my first interface!"""
    await console.print(container, "Hello, World!") # The actual command logic
```

The main program picks this up automatically, making it really easy for anyone (even me later!) to add new automation tasks without digging through complex UI code.

## Navigating Challenges: Hitting Python's Limits

Pretty soon, though, I ran into a couple of big hurdles that made me realize Python might not have been the _perfect_ choice for this specific tool, despite being great for getting started:

1.  **Sharing the Tool Was a Pain:** Python scripts need a Python interpreter to run. To share TF Utils with classmates who might not have Python set up (or the right libraries), I had to bundle it into an `.exe` file for Windows. Using tools like AutoPyToExe felt like black magic, involving specific DLLs and complicated build scripts that often only worked reliably on my own laptop. This also basically locked the tool to Windows.
2.  **Speed Over the Network:** The tool often needs to access project templates stored on our internal network drives. The Python version did this through the standard Windows file sharing, which could be noticeably slow, especially when copying lots of files.

Thinking about how to solve these issues led me to consider rewriting the tool in **Go (Golang)**. Go seemed like a good fit because:

1.  It compiles directly into a single executable file for Windows, Mac, or Linux. No complex bundling needed, making distribution way easier and truly cross-platform.
2.  Go is known for being fast, especially with network tasks. I could potentially use more direct methods like SFTP to talk to the server, hopefully speeding things up compared to going through Windows Explorer.

## The Outcome: Where It Stands and What I Learned

Right now, TF Utils (the Python version) is a working tool with a pretty nice TUI that does what I originally set out to do: automate common project setup tasks. It's documented, reasonably easy to add new commands to, and myself and a few friends in the program are actually using it regularly, which feels great! The build process is still clunky, but the tool itself is helpful.

You can check out the documentation here, which I put together using MkDocs with the Material theme: [https://imgajeed76.github.io/tfUtils/](https://imgajeed76.github.io/tfUtils/)

So, did I meet my goal? I think so. I wanted a structured way to simplify common tasks, and the current tool does that.

Along the way, I definitely learned a lot:

- Got much better at using Python decorators for cool things like automatically discovering functions.
- Figured out how to build decent TUIs with Textual.
- Got a real-world lesson in the pros and cons of different programming languages – Python is awesome for quick development, but compiled languages like Go can be much better for distribution and performance in certain situations.

I'm quite proud of how the TUI turned out and the modular system for adding commands. It feels pretty slick to use.

As mentioned, the next big idea is to actually build that V2 in Go. The plan is to tackle those distribution and speed problems head-on, making TF Utils even more useful and easier to share with everyone in the Electronics Technician program.
