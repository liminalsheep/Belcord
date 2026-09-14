"""Utilities for managing Discord bot scripts and lifecycle events.

Added Events:
    on_startup: Triggered once when the client becomes ready.
    on_closing: Triggered when `await client.close()` is called.
"""
__version__ = "0.1.1"
__all__ = ["trigger_event", "create_event", "remove_event"]

def wlc() -> None:
    import os, sys

    # Safe terminal width check with an 80-column fallback
    try:
        width = os.get_terminal_size().columns
    except OSError:
        width = 80 if sys.stdout.isatty() else 80

    # ANSI escape sequences
    blue, purple_bold, reset = "\033[94m", "\033[95m\033[1m", "\033[0m"

    # Pre-defined ASCII block
    banner = (
        " _____     _               _ ",
        "| __  |___| |___ ___ ___ _| |",
        "| __ -| -_| |  _| . |  _| . |",
        "|_____|___|_|___|___|_| |___|",
    )

    divider = f"{blue}{'—' * width}{reset}"
    art_centered = "\n".join(f"{purple_bold}{line.center(width)}{reset}" for line in banner)
    version_centered = f"Version {__version__}".center(width)

    print(f"{divider}\n{art_centered}\n{version_centered}\n{divider}")
wlc();del wlc

import asyncio
from warnings import warn
from ._event import trigger_event, create_event, remove_event


# --- Client Setup ---
client = None

def _configure(bot_client):
    from ._event import configure
    global client

    client = bot_client     # Set a global reference for the client object
    configure(client)       # Set up Belcord event manager

    from .plugin_manager import main
    asyncio.run(main())
