from src.lib.console import ask_input
from src.lib.interface import interface


#@interface("Test")
def test():
    print(ask_input("Test", "Test", placeholder="blabla", regex=r"^\d{3}$", error_message="Error\nlol"))