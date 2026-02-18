import discord
from discord.ext import commands

class SoloLevelingBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = False
        intents.members = True

        super().__init__(
            command_prefix=None,
            intents=intents,
        )

    async def setup_hook(self):
        await self.tree.sync()
        print("Slash commands synced.")

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
