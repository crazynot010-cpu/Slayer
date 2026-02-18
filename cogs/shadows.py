import discord
from discord import app_commands
from discord.ext import commands

from models.user_model import UserModel


class Shadows(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="shadows",
        description="View your shadow inventory"
    )
    async def shadows(
        self,
        interaction: discord.Interaction,
        member: discord.Member = None
    ):
        member = member or interaction.user

        user = await UserModel.get_user(
            member.id,
            interaction.guild.id
        )

        shadows = user["shadows"]

        if not shadows:
            await interaction.response.send_message(
                "⚠️ No shadows owned.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"{member.display_name}'s Shadows",
            color=0x2f3136
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        for shadow in shadows:
            embed.add_field(
                name=f"{shadow['name'].title()} [{shadow['rarity']}]",
                value=(
                    f"HP: {shadow['hp']}\n"
                    f"DEF: {shadow['defense']}\n"
                    f"ATK: {shadow['attack']}"
                ),
                inline=False
            )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Shadows(bot))
