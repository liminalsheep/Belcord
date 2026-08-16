"""Utilities for organizing Discord scripts and creating custom events.

Added events:
    on_startup():
        Called once when the client is ready.

    on_closing():
        Called when `await client.close()` is executed.
"""
__version__ = "0.2"
__all__ = ["trigger_event", "create_event", "remove_event"]


def wlc():
    import os
    try:
        w = os.get_terminal_size().columns
    except OSError:
        return
    lines = "\033[94m" + "—" * w
    print(
        lines,
        "\033[95m\033[1m" +
        " _____     _               _ ".center(w),
        "| __  |___| |___ ___ ___ _| |".center(w),
        "| __ -| -_| |  _| . |  _| . |".center(w),
        "|_____|___|_|___|___|_| |___|".center(w),

        "\033[0m" +
        f"Version {__version__}".center(w) + "\n",
        lines + "\033[0m",
        sep = "\n"
    )
wlc();del wlc


import asyncio
from warnings import warn
from ._event import trigger_event, create_event, remove_event


# --- Client Setup ---
client = None

def _configure(bot_client):
    from ._event import configure
    global client
    
    client = bot_client  # Set a global reference for the client object
    configure(client)  # Set up Belcord event manager

    from .plugin_manager import main
    asyncio.run(main())
