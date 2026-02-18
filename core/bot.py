import discord
from discord.ext import commands

from systems.spawn_system import spawn_system


class SlayerBot(commands.Bot):

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix="!",
            intents=intents
        )

    async def setup_hook(self):
        # Load cogs
        await self.load_extension("cogs.admin")
        await self.load_extension("cogs.arise")
        await self.load_extension("cogs.profile")
        await self.load_extension("cogs.hunt")
        await self.load_extension("cogs.leaderboard")
        await self.load_extension("cogs.shadows")

        # Sync slash commands globally
        await self.tree.sync()

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("Bot is ready.")

    async def on_message(self, message: discord.Message):
        await spawn_system.process_message(message)
        await self.process_commands(message)
