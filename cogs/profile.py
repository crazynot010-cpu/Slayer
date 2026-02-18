import discord
from discord import app_commands
from discord.ext import commands

from models.user_model import UserModel
from systems.xp_system import XPSystem
from utils.embeds import base_embed
from utils.helpers import format_number, progress_bar, rank_emoji


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # PREFIX COMMAND
    @commands.command(name="profile")
    async def profile_prefix(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        await self.send_profile(ctx, member)

    # SLASH COMMAND
    @app_commands.command(name="profile", description="View your hunter profile")
    async def profile_slash(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        await interaction.response.defer()
        await self.send_profile(interaction, member, slash=True)

    async def send_profile(self, ctx_or_interaction, member, slash=False):
        user = await UserModel.get_user(member.id)

        level = user["level"]
        xp = user["xp"]
        rank = user["rank"]
        gold = user["gold"]

        required = XPSystem.xp_required_for_level(level)

        embed = base_embed(
            title=f"{member.display_name}'s Hunter Profile"
        )

        embed.add_field(
            name="Rank",
            value=f"{rank_emoji(rank)} {rank}",
            inline=True
        )

        embed.add_field(
            name="Level",
            value=str(level),
            inline=True
        )

        embed.add_field(
            name="Gold",
            value=format_number(gold),
            inline=True
        )

        embed.add_field(
            name="XP",
            value=f"{progress_bar(xp, required)}\n{xp}/{required}",
            inline=False
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        if slash:
            await ctx_or_interaction.followup.send(embed=embed)
        else:
            await ctx_or_interaction.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Profile(bot))
