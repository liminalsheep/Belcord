"""Plugin manager CLI."""
__version__ = "1"

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
CACHE_EXPIRATION_SECONDS = 60*60*24*7  # 1 week in seconds


# --- Cache Helper ---

async def get_cached_tags(session: aiohttp.ClientSession) -> dict:
    """Fetches tags.json from repo/tags.json, caching it in __pycache__ for a week."""
    cache_dir = os.path.join(os.path.dirname(__file__), "__pycache__")
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, "tags.json")

    # Check if cache exists and is fresh
    if os.path.exists(cache_file):
        file_age = time.time() - os.path.getmtime(cache_file)
        if file_age < CACHE_EXPIRATION_SECONDS:
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass  # Fall back to refetching if cache is corrupt

    # Refetch tags
    url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/tags.json"
    try:
        async with session.get(url) as response:
            if response.status == 200:
                tags_data = await response.json(content_type=None)
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(tags_data, f, indent=2)
                return tags_data
            else:
                print(f"Error fetching tags: {response.status}")
    except Exception as e:
        print(f"Failed to fetch tags: {e}")

    return {"all": [], "plugins": {}}


# --- Local Plugin Helpers ---

def get_installed_manifest(plugin_name: str) -> dict | None:
    """Returns local manifest dict if the plugin is installed locally."""
    manifest_path = os.path.join(LOCAL_PLUGINS_DIR, plugin_name, "manifest.json")
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None
    return None


def get_plugin_status(plugin_name: str) -> str | None:
    """Returns 'enabled', 'disabled', or None if not installed."""
    manifest = get_installed_manifest(plugin_name)
    if manifest is None:
        return None
    return "enabled" if manifest.get("enabled", True) else "disabled"


def update_manifest_enabled(plugin_name: str, enabled: bool) -> bool:
    """Updates the 'enabled' key in local manifest.json."""
    manifest_path = os.path.join(LOCAL_PLUGINS_DIR, plugin_name, "manifest.json")
    if not os.path.exists(manifest_path):
        print(f"Plugin '{plugin_name}' is not installed.")
        return False

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


# --- Github API ---

async def get_plugins(session: aiohttp.ClientSession) -> list:
    """Fetches directory names using the public API endpoint."""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{PLUGINS_PATH}"

    async with session.get(url, headers=HEADERS) as response:
        if response.status != 200:
            print(f"Error fetching directory structure: {response.status}")
            return []
        contents = await response.json()
        return [item["name"] for item in contents if item["type"] == "dir"]


async def load_manifest(session: aiohttp.ClientSession, plugin_folder: str) -> dict:
    """Loads manifest.json directly from GitHub's raw content delivery network."""
    url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/{PLUGINS_PATH}/{plugin_folder}/manifest.json"

    async with session.get(url) as response:
        if response.status != 200:
            print(f"Could not find or load manifest for {plugin_folder}")
            return {}

        try:
            return await response.json(content_type=None)
        except json.JSONDecodeError:
            print(f"Invalid JSON in manifest for {plugin_folder}")
            return {}


async def download_file(session, download_url, local_path):
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


async def download_folder(session, folder_path, local_dir):
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
                download_url = item["download_url"]
                local_path = os.path.join(local_dir, item["name"])
                task = download_file(session, download_url, local_path)
                download_tasks.append(task)

            elif item["type"] == "dir":
                subfolder_remote_path = item["path"] 
                subfolder_local_path = os.path.join(local_dir, item["name"])
                task = download_folder(session, subfolder_remote_path, subfolder_local_path)
                download_tasks.append(task)

        if download_tasks:
            await asyncio.gather(*download_tasks)


# --- Formatting & Output Helpers ---

def format_plugin_display(plugin_name: str) -> str:
    """Formats a plugin name, appending status in parentheses if installed."""
    status = get_plugin_status(plugin_name)
    if status:
        return f"{plugin_name} ({status})"
    return plugin_name


def sort_plugins_installed_first(plugin_names: list[str]) -> list[str]:
    """Sorts plugins so installed ones are listed at the top."""
    installed = [p for p in plugin_names if get_plugin_status(p) is not None]
    uninstalled = [p for p in plugin_names if get_plugin_status(p) is None]
    return installed + uninstalled


def paginate_and_print(plugin_list: list[str], page_num: int, header_title: str, total_label: str = "matched"):
    """Handles sorting, pagination, and printing for plugin lists."""
    sorted_plugins = sort_plugins_installed_first(plugin_list)
    total_plugins = len(sorted_plugins)
    total_pages = max(1, math.ceil(total_plugins / PAGE_SIZE))

    page_num = max(1, min(page_num, total_pages))
    start_idx = (page_num - 1) * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    page_items = sorted_plugins[start_idx:end_idx]

    print(f"\n{header_title}")
    for plugin in page_items:
        print(f"* {format_plugin_display(plugin)}")

    print(f"\nPage {page_num} of {total_pages} • {total_plugins} {total_label}\n")


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

    page = 1
    if args[-1].isdigit():
        page = int(args.pop())

    search_tags = [t.lower() for t in args]
    tags_data = await get_cached_tags(session)
    plugin_tags_map = tags_data.get("plugins", {})

    matching_plugins = []
    for plugin_name, tags in plugin_tags_map.items():
        plugin_tags_lower = [t.lower() for t in tags]
        if all(tag in plugin_tags_lower for tag in search_tags):
            matching_plugins.append(plugin_name)

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
    local_dir = os.path.join(LOCAL_PLUGINS_DIR, plugin_name)

    print(f"Installing '{plugin_name}'...")
    await download_folder(session, remote_folder, local_dir)


async def cmd_enable(session: aiohttp.ClientSession, args: list[str]):
    if not args:
        print("Usage: enable <plugin_name1> [plugin_name2] ...")
        return

    for name in args:
        if update_manifest_enabled(name, True):
            print(f"Enabled plugin: {name}")


async def cmd_disable(session: aiohttp.ClientSession, args: list[str]):
    if not args:
        print("Usage: disable <plugin_name1> [plugin_name2] ...")
        return

    for name in args:
        if update_manifest_enabled(name, False):
            print(f"Disabled plugin: {name}")


async def cmd_uninstall(session: aiohttp.ClientSession, args: list[str]):
    if not args:
        print("Usage: uninstall <plugin_name1> [plugin_name2] ...")
        return

    for name in args:
        local_dir = os.path.join(LOCAL_PLUGINS_DIR, name)
        if os.path.exists(local_dir):
            try:
                shutil.rmtree(local_dir)
                print(f"Uninstalled plugin: {name}")
            except Exception as e:
                print(f"Failed to uninstall plugin '{name}': {e}")
        else:
            print(f"Plugin '{name}' is not installed.")


# --- Main Loop ---

COMMANDS = {
    "list": cmd_list,
    "tags": cmd_tags,
    "search": cmd_search,
    "install": cmd_install,
    "enable": cmd_enable,
    "disable": cmd_disable,
    "uninstall": cmd_uninstall,
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
