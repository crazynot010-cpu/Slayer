import discord
from discord import app_commands
from discord.ext import commands

from systems.spawn_system import SpawnSystem
from systems.xp_system import XPSystem
from systems.cooldown_system import CooldownSystem
from models.user_model import UserModel
from utils.embeds import base_embed, error_embed


class Hunt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # PREFIX
    @commands.command(name="hunt")
    async def hunt_prefix(self, ctx):
        await self.handle_hunt(ctx)

    # SLASH
    @app_commands.command(name="hunt", description="Hunt monsters to gain XP and gold")
    async def hunt_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.handle_hunt(interaction, slash=True)

    async def handle_hunt(self, ctx_or_interaction, slash=False):
        user_id = ctx_or_interaction.user.id if slash else ctx_or_interaction.author.id

        allowed, remaining = CooldownSystem.check(user_id, "hunt", 30)

        if not allowed:
            embed = error_embed(f"You must wait {remaining}s before hunting again.")
            if slash:
                await ctx_or_interaction.followup.send(embed=embed)
            else:
                await ctx_or_interaction.send(embed=embed)
            return

        monster = SpawnSystem.spawn()

        # Rewards
        xp = monster["xp"]
        gold = monster["gold"]

        await XPSystem.add_xp(user_id, xp)
        await UserModel.add_gold(user_id, gold)

        embed = base_embed(
            title="⚔️ Hunt Successful!",
            description=f"You defeated a **{monster['name']}**!"
        )

        embed.add_field(name="XP Gained", value=str(xp))
        embed.add_field(name="Gold Earned", value=str(gold))

        if slash:
            await ctx_or_interaction.followup.send(embed=embed)
        else:
            await ctx_or_interaction.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Hunt(bot))
