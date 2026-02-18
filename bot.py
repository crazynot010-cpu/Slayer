import discord
from discord.ext import commands


class SoloBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.members = True
        intents.message_content = True

        super().__init__(
            command_prefix="!",  # kept for admin fallback
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        cogs = [
            "cogs.spawn_cog",
            "cogs.arise_cog",
            "cogs.profile_cog",
            "cogs.leaderboard_cog",
            "cogs.admin_cog"
        ]

        for cog in cogs:
            await self.load_extension(cog)

        # Sync slash globally
        await self.tree.sync()
