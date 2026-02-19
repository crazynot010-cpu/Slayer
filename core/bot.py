import discord
from discord.ext import commands
from settings import PREFIX

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class MMORPG(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix=PREFIX,
            intents=intents
        )

    async def setup_hook(self):
        from core.player_commands import setup as player_setup
        await player_setup(self)

    async def on_ready(self):
        print(f"Logged in as {self.user}")
