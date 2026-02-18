import discord
from discord.ext import commands
import os
import asyncio


class SoloBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        # Load all cogs automatically
        await self.load_all_cogs()

        # Sync slash commands globally
        await self.tree.sync()
        print("Slash commands synced.")

    async def load_all_cogs(self):
        for root, _, files in os.walk("cogs"):
            for file in files:
                if file.endswith(".py") and not file.startswith("__"):
                    path = os.path.join(root, file)
                    extension = path.replace("\\", ".").replace("/", ".")[:-3]
                    try:
                        await self.load_extension(extension)
                        print(f"Loaded extension: {extension}")
                    except Exception as e:
                        print(f"Failed to load {extension}: {e}")

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("Bot is ready.")
