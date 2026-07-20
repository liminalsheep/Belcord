# Belcord
Discord bot development just as applying mods to a videogame.
You can submit your plugins at my Discord server: **[BUSSIN'](<https://discord.gg/3pT2S7czUR>)**

## 🛠️ Plugin Management

Since plugin features are fully implemented on startup, you can immediately browse, install, and manage your plugins using the commands below.

### 1. Browse Plugins
You can view the complete list of available plugins or filter them using tags.

#### View All Plugins
To see everything available, run the following command:

```bash
list [page_number]
```
*Note: The `[page_number]` argument is optional.*

**Example Output:**
> 📄 **Available Plugins**
> * `custom_presence` (enabled)
> * `moderation_commands` (enabled)
> * ...
> 
> Page 1 of 2 • 13 plugins total

---

#### Search by Tags
If you are looking for specific functionality, you can filter plugins by their tags.

1. **Find available tags:** First, see what categories exist by running:
```bash
tags
```
2. **Filter your search:** Use one or more tags to find matching plugins:
```bash
search <tag1> [tag2] ... [page_number]
```

**Example Output:**
> 🔍 **Search Results**
> * `clipboard`
> * `utilities`
> * ...
> 
> Page 1 of 2 • 8 plugins matched

### 2. Plugin Installation
Once you have found the plugin you want, you can install it directly using its name.

#### Install a Plugin
Run the installation command followed by the exact name of the plugin:

```bash
install <plugin_name>
```

**Example:**
```bash
install moderation_commands
```

### 3. Managing Plugins (Enable, Disable & Uninstall)
Once a plugin is installed, you can toggle its status or completely remove it.

#### Enable Plugins
If a plugin is disabled, you can re-activate it by running:

```bash
enable <plugin_name1> [plugin_name2] ...
```

#### Disable Plugins
If you want to temporarily turn off a plugin without completely deleting its files, disable it by running:

```bash
disable <plugin_name1> [plugin_name2] ...
```

#### Uninstall Plugins
To completely remove a plugin from your bot, run the uninstallation command:

```bash
uninstall <plugin_name1> [plugin_name2] ...
```

**Example:**
```bash
uninstall custom_presence
```

### 4. Updating Plugins

You can check for updates across all installed plugins and upgrade them either individually or all at once.

#### Check Upgradable Plugins
To view a list of installed plugins that have a newer version available remotely:

```bash
upgradable
```

**Example Output:**
> 🚀 **Upgradable Plugins:**
> * `moderation_commands` (current: 1.0 -> latest: 1.2)
> * `utilities` (current: 0.9 -> latest: 1.0)

#### Upgrade Plugins
To update specific plugins or all upgradable plugins at once, use:

```bash
upgrade <plugin_name1> [plugin_name2] ...
```

To upgrade all installed plugins that have updates available:

```bash
upgrade all
```
