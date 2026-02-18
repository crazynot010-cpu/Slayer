import discord
from discord import app_commands
from discord.ext import commands

from models.user_model import UserModel
from utils.embeds import base_embed


class Shadows(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # PREFIX
    @commands.command(name="shadows")
    async def shadows_prefix(self, ctx):
        await self.send_shadows(ctx)

    # SLASH
    @app_commands.command(name="shadows", description="View your shadow army")
    async def shadows_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.send_shadows(interaction, slash=True)

    async def send_shadows(self, ctx_or_interaction, slash=False):
        user_id = ctx_or_interaction.user.id if slash else ctx_or_interaction.author.id
        user = await UserModel.get_user(user_id)

        shadows = user["shadows"]

        embed = base_embed(title="🖤 Your Shadow Army")

        if not shadows:
            embed.description = "You have no shadows yet."
        else:
            for shadow in shadows:
                embed.add_field(
                    name=shadow["name"],
                    value=f"Rank: {shadow['rank']}",
                    inline=False
                )

        if slash:
            await ctx_or_interaction.followup.send(embed=embed)
        else:
            await ctx_or_interaction.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Shadows(bot))
