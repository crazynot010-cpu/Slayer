import discord
from discord.ext import commands
from discord import app_commands

from models.user_model import UserModel
from utils.embeds import base_embed


class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # PREFIX
    @commands.command(name="leaderboard", aliases=["lb"])
    async def leaderboard_prefix(self, ctx, category: str = "level"):
        await self.send_leaderboard(ctx, category)

    # SLASH
    @app_commands.command(name="leaderboard", description="View global rankings")
    @app_commands.describe(category="Choose ranking category: level or gold")
    async def leaderboard_slash(self, interaction: discord.Interaction, category: str = "level"):
        await interaction.response.defer()
        await self.send_leaderboard(interaction, category, slash=True)

    async def send_leaderboard(self, ctx_or_interaction, category: str, slash=False):
        category = category.lower()

        if category not in ["level", "gold"]:
            embed = base_embed(title="Invalid Category")
            embed.description = "Available categories: `level`, `gold`"
            if slash:
                await ctx_or_interaction.followup.send(embed=embed)
            else:
                await ctx_or_interaction.send(embed=embed)
            return

        # Get sorted users from DB
        users = await UserModel.get_top_users(category)

        embed = base_embed(title=f"🏆 Global {category.capitalize()} Leaderboard")

        if not users:
            embed.description = "No data available yet."
        else:
            for index, user in enumerate(users[:10], start=1):
                embed.add_field(
                    name=f"#{index}",
                    value=f"<@{user['user_id']}> — {user.get(category, 0)}",
                    inline=False
                )

        if slash:
            await ctx_or_interaction.followup.send(embed=embed)
        else:
            await ctx_or_interaction.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
