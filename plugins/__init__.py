"""Set up Belcord environment.

Usage:
    import plugins
    scripts.init(client: discord.Client)
"""
__version__ = "0.2"


def init(client: "discord.Client"):
    """
    Initializes Belcord and imports the modules in your plugins folder.

    Appends the scripts folder to the system path and changes the current
    working directory to `./data`.
    """
    import os, sys, json

    # Remove the home dir path, add plugins path and change the current
    # working directory
    path = os.path.dirname(__file__)
    cwd = os.path.dirname(path)
    data = os.path.join(cwd, "data")

    try:
        sys.path.remove(cwd)
    except ValueError:
        pass
    sys.path.insert(0, path)
    os.makedirs(data, exist_ok=True)
    os.chdir(data)

    from belcord import _configure
    _configure(client)

    # --- Load plugins ---

    # Get every plugin
    scripts_path = os.path.dirname(__file__)
    scripts = {
        d: None for d in os.listdir(scripts_path)
        if not d.startswith("_")
        and os.path.isfile(os.path.join(scripts_path, d, "manifest.json"))
    }
    scripts.pop("belcord", None)
    last = []

    # Check enabled plugins and load layer
    for s in scripts.copy():
        with open(
            os.path.join(scripts_path, s, "manifest.json"),
            "r", encoding="utf-8"
        ) as f:
            manifest = json.load(f)
            if manifest.get("enabled", False):
                if (load_layer := manifest.get("load_layer", -1)) < 0:
                    last.append(s)
                    del scripts[s]
                else:
                    scripts[s] = load_layer
            else:
                del scripts[s]

    # Sort by load layer
    scripts = [
        i[0] for i in
        sorted(scripts.items(), key=lambda x: x[1])
    ] + last

    # Load selected scripts
    for s in scripts:
        __import__(s)
