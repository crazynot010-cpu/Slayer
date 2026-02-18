import discord
from discord import app_commands
from discord.ext import commands

from models.user_model import UserModel
from systems.xp_system import XPSystem


class Profile(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="profile",
        description="View your hunter profile"
    )
    async def profile(
        self,
        interaction: discord.Interaction,
        member: discord.Member = None
    ):
        member = member or interaction.user

        user = await UserModel.get_user(
            member.id,
            interaction.guild.id
        )

        xp_needed = XPSystem.xp_needed(user["level"])
        shadow_count = len(user["shadows"])

        embed = discord.Embed(
            title=f"{member.display_name}'s Hunter Profile",
            color=0x2f3136
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        embed.add_field(
            name="Level",
            value=user["level"],
            inline=True
        )

        embed.add_field(
            name="XP",
            value=f"{user['xp']} / {xp_needed}",
            inline=True
        )

        embed.add_field(
            name="Shadows",
            value=shadow_count,
            inline=True
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Profile(bot))
