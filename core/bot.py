import discord
from discord.ext import commands
from discord import app_commands

from models.shadow_model import ShadowModel
from models.user_model import UserModel
from models.guild_model import GuildModel
from systems.spawn_system import SpawnSystem
from systems.arise_system import AriseSystem
from systems.xp_system import XPSystem

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

        self.spawn_cooldowns = {}

    # =====================================================
    # GLOBAL SYNC ONLY
    # =====================================================
    async def setup_hook(self):
        synced = await self.tree.sync()
        print(f"Global synced {len(synced)} commands.")

    # =====================================================
    # READY
    # =====================================================
    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")

    # =====================================================
    # GLOBAL SLASH ERROR HANDLER
    # =====================================================
    async def on_app_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        print(f"Slash Error: {error}")

        if interaction.response.is_done():
            await interaction.followup.send(
                "An internal error occurred.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "An internal error occurred.",
                ephemeral=True
            )

    # =====================================================
    # XP SYSTEM
    # =====================================================
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        await XPSystem.add_xp(
            user_id=message.author.id,
            guild_id=message.guild.id,
            amount=XP_PER_MESSAGE
        )

        await self.process_commands(message)

    # =====================================================
    # ADD SHADOW
    # =====================================================
    @app_commands.command(name="addshadow", description="Add a new shadow")
    async def addshadow(
        self,
        interaction: discord.Interaction,
        name: str,
        rank: str,
        hp: int,
        attack: int
    ):
        await interaction.response.defer()

        await ShadowModel.create_shadow(name, rank, hp, attack)

        await interaction.followup.send(
            f"Shadow **{name}** added."
        )

    # =====================================================
    # REMOVE SHADOW
    # =====================================================
    @app_commands.command(name="removeshadow", description="Remove shadow")
    async def removeshadow(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer()

        await ShadowModel.delete_shadow(name)

        await interaction.followup.send(
            f"Shadow **{name}** removed."
        )

    # =====================================================
    # SHADOW STATS
    # =====================================================
    @app_commands.command(name="statsshdw", description="View shadow stats")
    async def statsshdw(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer()

        shadow = await ShadowModel.get_shadow(name)

        if not shadow:
            return await interaction.followup.send("Shadow not found.")

        await interaction.followup.send(
            f"**{shadow['name']}**\n"
            f"Rank: {shadow['rank']}\n"
            f"HP: {shadow['hp']}\n"
            f"ATK: {shadow['attack']}"
        )

    # =====================================================
    # SET SPAWN CHANNEL
    # =====================================================
    @app_commands.command(name="setspawnchannel", description="Set spawn channel")
    async def setspawnchannel(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):
        await interaction.response.defer()

        await GuildModel.set_spawn_channel(
            interaction.guild.id,
            channel.id
        )

        await interaction.followup.send(
            f"Spawn channel set to {channel.mention}"
        )

    # =====================================================
    # SET SPAWN PING
    # =====================================================
    @app_commands.command(name="setspawnping", description="Set spawn ping role")
    async def setspawnping(
        self,
        interaction: discord.Interaction,
        role: discord.Role
    ):
        await interaction.response.defer()

        await GuildModel.set_spawn_ping(
            interaction.guild.id,
            role.id
        )

        await interaction.followup.send(
            f"Spawn ping set to {role.mention}"
        )

    # =====================================================
    # ARISE (MAX DUPE = 3)
    # =====================================================
    @app_commands.command(name="arise", description="Capture a shadow")
    async def arise(self, interaction: discord.Interaction):
        await interaction.response.defer()

        result = await AriseSystem.capture_shadow(
            interaction.user.id,
            interaction.guild.id
        )

        await interaction.followup.send(result)

    # =====================================================
    # PROFILE
    # =====================================================
    @app_commands.command(name="profile", description="View your profile")
    async def profile(self, interaction: discord.Interaction):
        await interaction.response.defer()

        user = await UserModel.get_user(
            interaction.user.id,
            interaction.guild.id
        )

        if not user:
            return await interaction.followup.send("Profile not found.")

        await interaction.followup.send(
            f"Level: {user['level']}\n"
            f"XP: {user['xp']}"
        )

    # =====================================================
    # SET BACKGROUND
    # =====================================================
    @app_commands.command(name="setbackground", description="Set profile background")
    async def setbackground(self, interaction: discord.Interaction, url: str):
        await interaction.response.defer()

        await UserModel.set_background(
            interaction.user.id,
            interaction.guild.id,
            url
        )

        await interaction.followup.send("Background updated.")

    # =====================================================
    # INVENTORY
    # =====================================================
    @app_commands.command(name="inventory", description="View your shadows")
    async def inventory(self, interaction: discord.Interaction):
        await interaction.response.defer()

        shadows = await UserModel.get_inventory(
            interaction.user.id,
            interaction.guild.id
        )

        if not shadows:
            return await interaction.followup.send("Inventory empty.")

        formatted = "\n".join(
            [f"{name} x{count}" for name, count in shadows.items()]
        )

        await interaction.followup.send(
            f"**Your Shadows:**\n{formatted}"
        )

    # =====================================================
    # LEADERBOARD
    # =====================================================
    @app_commands.command(name="leaderboard", description="XP leaderboard")
    async def leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer()

        top = await UserModel.get_leaderboard(interaction.guild.id)

        if not top:
            return await interaction.followup.send("No data yet.")

        lines = []
        for i, user in enumerate(top, start=1):
            lines.append(
                f"{i}. <@{user['user_id']}> — Level {user['level']}"
            )

        await interaction.followup.send(
            "**Leaderboard**\n" + "\n".join(lines)
        )
