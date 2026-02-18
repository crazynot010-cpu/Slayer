import discord
from discord import app_commands
from discord.ext import commands

from models.user_model import UserModel


class Profile(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="profile",
        description="View your hunter profile"
    )
    async def profile(self, interaction: discord.Interaction):

        await interaction.response.defer()

        user = await UserModel.get_user(
            user_id=interaction.user.id,
            guild_id=interaction.guild.id
        )

        await interaction.followup.send(
            f"🏹 **Hunter Profile**\n\n"
            f"Level: {user['level']}\n"
            f"XP: {user['xp']}\n"
            f"Shadows: {len(user['shadows'])}"
        )


async def setup(bot):
    await bot.add_cog(Profile(bot))
