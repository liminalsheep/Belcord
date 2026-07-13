def main():
    """Prepare Belcord environment."""

    # Create bot instance
    from discord import Client, Intents
    bot = Client(intents=Intents.all())

    # --- Setup Belcord ----
    # Initialize environment
    import plugins
    plugins.init(bot)

    return bot


if __name__ == "__main__":
    bot = main()
    bot.run("YOUR_BOT_TOKEN")
