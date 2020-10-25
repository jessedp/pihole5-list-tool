""" silly ansi banner"""

from colors import color
import utils

__version__ = "0.6.0"


def display():
    """ duisplay the banner """
    print(color("    ┌──────────────────────────────────────────┐", fg="#b61042"))
    print(
        color("    │       ", fg="#b61042")
        + color(f"π-hole 5 list tool  v{__version__}", "#FFF")
        + color("         │", fg="#b61042")
    )
    print(color("    └──────────────────────────────────────────┘", fg="#b61042"))
    utils.info("    https://github.com/jessedp/pihole5-list-tool\n")
