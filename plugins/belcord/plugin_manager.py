"""Plugin manager CLI."""
__version__ = "1.2"

import aiohttp
import asyncio
import json
import math
import os
import shlex
import shutil
import time

REPO_OWNER = "liminalsheep"
REPO_NAME = "Belcord-plugins"
PLUGINS_PATH = "plugins"
LOCAL_PLUGINS_DIR = os.path.dirname(os.path.dirname(__file__))

HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "Mozilla/5.0"
}

PAGE_SIZE = 10
CACHE_EXPIRATION_SECONDS = 60 * 60 * 24


# --- Cache Helpers ---

def get_cache_dir() -> str:
    """Ensures and returns the path to the __pycache__ directory."""
    cache_dir = os.path.join(os.path.dirname(__file__), "__pycache__")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


async def fetch_json_cached(session: aiohttp.ClientSession, filename: str, url: str, fallback_data: dict | list, headers: dict | None = None) -> dict | list:
    """Generic JSON caching wrapper for GET requests."""
    cache_file = os.path.join(get_cache_dir(), filename)

    if os.path.exists(cache_file):
        if time.time() - os.path.getmtime(cache_file) < CACHE_EXPIRATION_SECONDS:
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass  # Fall back to fetching if cache is corrupt

    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json(content_type=None)
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                return data
            print(f"Error fetching {filename}: HTTP {response.status}")
    except Exception as e:
        print(f"Failed to fetch {filename}: {e}")

    # Fallback attempt on failure: try reading expired/corrupted cache before using fallback_data
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass

    return fallback_data


async def get_cached_tags(session: aiohttp.ClientSession) -> dict:
    url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/tags.json"
    return await fetch_json_cached(session, "tags.json", url, fallback_data={"all": [], "plugins": {}})


# --- Local Plugin Helpers ---

def get_plugin_path(plugin_name: str) -> str | None:
    """Locates local plugin directory containing a manifest.json."""
    candidates = [
        os.path.join(LOCAL_PLUGINS_DIR, PLUGINS_PATH, plugin_name),
        os.path.join(LOCAL_PLUGINS_DIR, plugin_name)
    ]
    for path in candidates:
        if os.path.exists(os.path.join(path, "manifest.json")):
            return path
    return None


def get_installed_plugins() -> list[str]:
    """Returns a list of folder names for locally installed plugins."""
    search_dirs = [
        os.path.join(LOCAL_PLUGINS_DIR, PLUGINS_PATH),
        LOCAL_PLUGINS_DIR
    ]
    installed = set()
    for base_dir in search_dirs:
        if os.path.exists(base_dir):
            for entry in os.listdir(base_dir):
                if os.path.exists(os.path.join(base_dir, entry, "manifest.json")):
                    installed.add(entry)
    return list(installed)


def get_installed_manifest(plugin_name: str) -> dict | None:
    """Returns local manifest dict if the plugin is installed locally."""
    path = get_plugin_path(plugin_name)
    if not path:
        return None
    try:
        with open(os.path.join(path, "manifest.json"), "r", encoding="utf-8") as f:
            manifest = json.load(f)
            if plugin_name.lower() == "belcord":
                manifest["enabled"] = True
            return manifest
    except (json.JSONDecodeError, OSError):
        return None


def get_plugin_status(plugin_name: str) -> str | None:
    """Returns 'enabled', 'disabled', or None if not installed."""
    manifest = get_installed_manifest(plugin_name)
    if manifest is None:
        return None
    return "enabled" if manifest.get("enabled", True) else "disabled"


def update_manifest_enabled(plugin_name: str, enabled: bool) -> bool:
    """Updates the 'enabled' key in local manifest.json."""
    if plugin_name.lower() == "belcord":
        print("Plugin 'belcord' is always enabled and cannot be toggled.")
        return False

    path = get_plugin_path(plugin_name)
    if not path:
        print(f"Plugin '{plugin_name}' is not installed.")
        return False

    manifest_path = os.path.join(path, "manifest.json")
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        manifest["enabled"] = enabled

        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        return True
    except Exception as e:
        print(f"Failed to update manifest for '{plugin_name}': {e}")
        return False


# --- GitHub API ---

async def get_plugins(session: aiohttp.ClientSession) -> list[str]:
    """Fetches plugin list from GitHub, caching in __pycache__/plugins.json."""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{PLUGINS_PATH}"
    result = await fetch_json_cached(session, "plugins.json", url, fallback_data=None, headers=HEADERS)

    if isinstance(result, list):
        # GitHub contents endpoint returns a list of items
        if result and isinstance(result[0], dict) and "name" in result[0]:
            return [item["name"] for item in result if item.get("type") == "dir"]
        # If loaded from cache, it's already a simple list of strings
        return result

    return get_installed_plugins()


async def load_manifest(session: aiohttp.ClientSession, plugin_folder: str) -> dict:
    """Loads manifest.json directly from GitHub's raw content delivery network."""
    url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/{PLUGINS_PATH}/{plugin_folder}/manifest.json"
    try:
        async with session.get(url) as response:
            if response.status != 200:
                print(f"Could not find or load manifest for {plugin_folder}")
                return {}
            manifest = await response.json(content_type=None)
            if plugin_folder.lower() == "belcord":
                manifest["enabled"] = True
            return manifest
    except (aiohttp.ClientError, json.JSONDecodeError):
        print(f"Invalid JSON or connection error in manifest for {plugin_folder}")
        return {}


async def download_file(session: aiohttp.ClientSession, download_url: str, local_path: str):
    """Downloads an individual file from a raw URL."""
    try:
        async with session.get(download_url, headers=HEADERS) as response:
            if response.status == 200:
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                content = await response.read()

                # Inject enabled = true if downloading manifest.json
                if os.path.basename(local_path) == "manifest.json":
                    try:
                        manifest = json.loads(content.decode("utf-8"))
                        manifest["enabled"] = True
                        content = json.dumps(manifest, indent=2).encode("utf-8")
                    except Exception:
                        pass

                with open(local_path, "wb") as f:
                    f.write(content)
                print(f"Downloaded: {local_path}")
            else:
                print(f"Failed to download file {local_path}: {response.status}")
    except Exception as e:
        print(f"Error downloading {local_path}: {e}")


async def download_folder(session: aiohttp.ClientSession, folder_path: str, local_dir: str):
    """Recursively fetches directory contents and downloads files/folders."""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{folder_path}"

    async with session.get(url, headers=HEADERS) as response:
        if response.status != 200:
            print(f"Failed to fetch directory contents for '{folder_path}': {response.status}")
            return

        items = await response.json()
        download_tasks = []

        for item in items:
            if item["type"] == "file":
                local_path = os.path.join(local_dir, item["name"])
                download_tasks.append(download_file(session, item["download_url"], local_path))
            elif item["type"] == "dir":
                subfolder_local_path = os.path.join(local_dir, item["name"])
                download_tasks.append(download_folder(session, item["path"], subfolder_local_path))

        if download_tasks:
            await asyncio.gather(*download_tasks)


# --- Formatting & Output Helpers ---

def format_plugin_display(plugin_name: str) -> str:
    """Formats a plugin name, appending status in parentheses if installed."""
    status = get_plugin_status(plugin_name)
    return f"{plugin_name} ({status})" if status else plugin_name


def sort_plugins_installed_first(plugin_names: list[str]) -> list[str]:
    """Sorts plugins so 'belcord' is at the very top, then installed, then uninstalled."""
    belcord_plugins = [p for p in plugin_names if p.lower() == "belcord"]
    other_plugins = [p for p in plugin_names if p.lower() != "belcord"]

    installed = [p for p in other_plugins if get_plugin_status(p) is not None]
    uninstalled = [p for p in other_plugins if get_plugin_status(p) is None]

    return belcord_plugins + installed + uninstalled


def paginate_and_print(plugin_list: list[str], page_num: int, header_title: str, total_label: str = "matched"):
    """Handles sorting, pagination, and printing for plugin lists."""
    sorted_plugins = sort_plugins_installed_first(plugin_list)
    total_plugins = len(sorted_plugins)
    total_pages = max(1, math.ceil(total_plugins / PAGE_SIZE))

    page_num = max(1, min(page_num, total_pages))
    start_idx = (page_num - 1) * PAGE_SIZE
    page_items = sorted_plugins[start_idx:start_idx + PAGE_SIZE]

    print(f"\n{header_title}")
    for plugin in page_items:
        print(f"* {format_plugin_display(plugin)}")

    print(f"\nPage {page_num} of {total_pages} • {total_plugins} {total_label}\n")


async def fetch_upgradable_plugins(session: aiohttp.ClientSession) -> list[tuple[str, str, str]]:
    """Checks all locally installed plugins against their remote manifests."""
    installed = get_installed_plugins()
    upgradable = []

    for name in installed:
        local_manifest = get_installed_manifest(name) or {}
        remote_manifest = await load_manifest(session, name)

        if not remote_manifest:
            continue

        current_version = str(local_manifest.get("version") or local_manifest.get("plugin_version") or "0")
        remote_version = str(remote_manifest.get("version") or remote_manifest.get("plugin_version") or "0")

        if current_version != remote_version:
            upgradable.append((name, current_version, remote_version))

    return upgradable


# --- CLI Commands ---

async def cmd_list(session: aiohttp.ClientSession, args: list[str]):
    page = int(args[0]) if args and args[0].isdigit() else 1
    plugins = await get_plugins(session)
    if not plugins:
        print("No plugins available.")
        return
    paginate_and_print(plugins, page, "📄 Available Plugins", total_label="plugins total")


async def cmd_tags(session: aiohttp.ClientSession, args: list[str]):
    tags_data = await get_cached_tags(session)
    all_tags = tags_data.get("all", [])

    if not all_tags:
        print("No tags available.")
        return

    print("\n🏷️ Available Tags")
    for tag in all_tags:
        print(f"* {tag}")
    print()


async def cmd_search(session: aiohttp.ClientSession, args: list[str]):
    if not args:
        print("Usage: search <tag1> [tag2] ... [page_number]")
        return

    page = int(args.pop()) if args[-1].isdigit() else 1
    search_tags = [t.lower() for t in args]
    tags_data = await get_cached_tags(session)
    plugin_tags_map = tags_data.get("plugins", {})

    matching_plugins = [
        plugin_name for plugin_name, tags in plugin_tags_map.items()
        if all(tag in [t.lower() for t in tags] for tag in search_tags)
    ]

    if not matching_plugins:
        print("No matching plugins found.")
        return

    paginate_and_print(matching_plugins, page, "🔍 Search Results", total_label="matched")


async def cmd_install(session: aiohttp.ClientSession, args: list[str]):
    if not args:
        print("Usage: install <plugin_name>")
        return

    plugin_name = args[0]
    remote_folder = f"{PLUGINS_PATH}/{plugin_name}"
    local_dir = os.path.join(LOCAL_PLUGINS_DIR, PLUGINS_PATH, plugin_name)

    print(f"Installing '{plugin_name}'...")
    await download_folder(session, remote_folder, local_dir)


def _toggle_plugins(args: list[str], enable_state: bool, state_label: str):
    if not args:
        print(f"Usage: {state_label.lower()} <plugin_name1> [plugin_name2] ...")
        return
    for name in args:
        if update_manifest_enabled(name, enable_state):
            print(f"{state_label} plugin: {name}")


async def cmd_enable(session: aiohttp.ClientSession, args: list[str]):
    _toggle_plugins(args, True, "Enabled")


async def cmd_disable(session: aiohttp.ClientSession, args: list[str]):
    _toggle_plugins(args, False, "Disabled")


async def cmd_uninstall(session: aiohttp.ClientSession, args: list[str]):
    if not args:
        print("Usage: uninstall <plugin_name1> [plugin_name2] ...")
        return

    for name in args:
        path = get_plugin_path(name)
        if path and os.path.exists(path):
            try:
                shutil.rmtree(path)
                print(f"Uninstalled plugin: {name}")
            except Exception as e:
                print(f"Failed to uninstall plugin '{name}': {e}")
        else:
            print(f"Plugin '{name}' is not installed.")


async def cmd_upgradable(session: aiohttp.ClientSession, args: list[str]):
    print("Checking for updates...")
    upgradable_list = await fetch_upgradable_plugins(session)

    if not upgradable_list:
        print("All plugins are up to date.")
        return

    print("\n🚀 Upgradable Plugins:")
    for name, curr, remote in upgradable_list:
        print(f"* {name} (current: {curr} -> latest: {remote})")
    print()


async def cmd_upgrade(session: aiohttp.ClientSession, args: list[str]):
    if not args:
        print("Usage: upgrade <plugin_name1> [plugin_name2] ... or 'upgrade all'")
        return

    plugins_to_upgrade = list(args)

    if len(plugins_to_upgrade) == 1 and plugins_to_upgrade[0].lower() == "all":
        print("Checking for upgradable plugins...")
        upgradable_info = await fetch_upgradable_plugins(session)
        if not upgradable_info:
            print("No plugins require upgrading.")
            return
        plugins_to_upgrade = [item[0] for item in upgradable_info]

    for name in plugins_to_upgrade:
        if not get_plugin_status(name):
            print(f"Plugin '{name}' is not currently installed. Use 'install {name}' instead.")
            continue

        print(f"Upgrading '{name}'...")
        remote_folder = f"{PLUGINS_PATH}/{name}"
        local_dir = get_plugin_path(name) or os.path.join(LOCAL_PLUGINS_DIR, PLUGINS_PATH, name)
        await download_folder(session, remote_folder, local_dir)
        print(f"Successfully upgraded '{name}'.")


# --- Main Loop ---

COMMANDS = {
    "list": cmd_list,
    "tags": cmd_tags,
    "search": cmd_search,
    "install": cmd_install,
    "enable": cmd_enable,
    "disable": cmd_disable,
    "uninstall": cmd_uninstall,
    "upgradable": cmd_upgradable,
    "upgrade": cmd_upgrade,
}


async def main():
    async with aiohttp.ClientSession() as session:
        print(
            "Belcord Plugin Manager CLI (press ENTER to initialize)\n"
            f"Commands: {', '.join(COMMANDS.keys())}"
        )
        while True:
            try:
                user_input = input("> ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nExiting...")
                break

            if not user_input:
                break

            tokens = shlex.split(user_input)
            cmd, args = tokens[0].lower(), tokens[1:]

            handler = COMMANDS.get(cmd)
            if handler:
                await handler(session, args)
            else:
                print(f"Unknown command: '{cmd}'.")


if __name__ == "__main__":
    asyncio.run(main())
