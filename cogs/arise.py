import discord
from discord import app_commands
from discord.ext import commands

from systems.spawn_system import SpawnSystem
from systems.arise_system import AriseSystem
from models.user_model import UserModel
from utils.embeds import base_embed, error_embed, success_embed
from utils.constants import MAX_SHADOWS


class Arise(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # PREFIX
    @commands.command(name="arise")
    async def arise_prefix(self, ctx):
        await self.handle_arise(ctx)

    # SLASH
    @app_commands.command(name="arise", description="Attempt to arise your last defeated monster")
    async def arise_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.handle_arise(interaction, slash=True)

    async def handle_arise(self, ctx_or_interaction, slash=False):
        user_id = ctx_or_interaction.user.id if slash else ctx_or_interaction.author.id

        last_monster = SpawnSystem.get_last_defeated(user_id)

        if not last_monster:
            embed = error_embed("You have no defeated monster to arise.")
            if slash:
                await ctx_or_interaction.followup.send(embed=embed)
            else:
                await ctx_or_interaction.send(embed=embed)
            return

        user = await UserModel.get_user(user_id)

        if len(user["shadows"]) >= MAX_SHADOWS:
            embed = error_embed("You have reached maximum shadow capacity.")
            if slash:
                await ctx_or_interaction.followup.send(embed=embed)
            else:
                await ctx_or_interaction.send(embed=embed)
            return

        success = AriseSystem.attempt(user_id, last_monster)

        if not success:
            embed = error_embed("The shadow resisted your command...")
        else:
            embed = success_embed(f"{last_monster['name']} has arisen as your shadow!")

        if slash:
            await ctx_or_interaction.followup.send(embed=embed)
        else:
            await ctx_or_interaction.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Arise(bot))
