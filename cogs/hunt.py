import discord
from discord import app_commands
from discord.ext import commands

from systems.spawn_system import spawn_system
from models.guild_model import GuildModel


class Hunt(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="hunt",
        description="Force spawn a shadow (Admin only)"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def hunt(self, interaction: discord.Interaction):

        guild_data = await GuildModel.get_guild(interaction.guild.id)

        if not guild_data["spawn_channel_id"]:
            await interaction.response.send_message(
                "❌ Spawn channel not set.",
                ephemeral=True
            )
            return

        channel = interaction.guild.get_channel(
            guild_data["spawn_channel_id"]
        )

        if not channel:
            await interaction.response.send_message(
                "❌ Spawn channel invalid.",
                ephemeral=True
            )
            return

        await spawn_system.spawn_shadow(channel, interaction.guild)

        await interaction.response.send_message(
            "⚔️ Shadow spawned manually."
        )


async def setup(bot):
    await bot.add_cog(Hunt(bot))
