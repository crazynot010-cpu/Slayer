import discord
from discord.ext import commands

from systems.xp_system import add_xp

XP_PER_MESSAGE = 25


class SoloLevelingBot(commands.Bot):

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix="!",
            intents=intents
        )

    # ===============================
    # LOAD COGS + GLOBAL SYNC
    # ===============================
    async def setup_hook(self):

        # Load all cogs
        await self.load_extension("cogs.profile")
        await self.load_extension("cogs.hunt")
        await self.load_extension("cogs.arise")
        await self.load_extension("cogs.leaderboard")
        await self.load_extension("cogs.admin")
        await self.load_extension("cogs.shadows")

        # Global sync AFTER loading
        synced = await self.tree.sync()
        print(f"Globally synced {len(synced)} commands.")

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")

    # ===============================
    # XP SYSTEM
    # ===============================
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        await add_xp(
            user_id=message.author.id,
            guild_id=message.guild.id,
            amount=XP_PER_MESSAGE
        )

        await self.process_commands(message)

    # ===============================
    # GLOBAL ERROR HANDLER
    # ===============================
    async def on_app_command_error(self, interaction, error):
        print("Slash Error:", error)

        if interaction.response.is_done():
            await interaction.followup.send(
                "An error occurred.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "An error occurred.",
                ephemeral=True
            )
