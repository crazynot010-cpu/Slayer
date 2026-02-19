from discord.ext import commands
import discord
from systems.player_system import PlayerSystem
from systems.xp_system import XPSystem
from utils.embeds import success_embed

class PlayerCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def profile(self, ctx):
        player = await PlayerSystem.get_player(ctx.author.id)

        embed = discord.Embed(
            title=f"{ctx.author.name}'s Profile",
            color=0x3498db
        )

        embed.add_field(name="Level", value=player["level"])
        embed.add_field(name="XP", value=player["xp"])
        embed.add_field(name="HP", value=f'{player["hp"]}/{player["max_hp"]}')
        embed.add_field(name="Attack", value=player["attack"])
        embed.add_field(name="Defense", value=player["defense"])
        embed.add_field(name="Money", value=player["money"])

        await ctx.send(embed=embed)

    @commands.command()
    async def train(self, ctx):
        await PlayerSystem.add_xp(ctx.author.id, 50)

        player = await PlayerSystem.get_player(ctx.author.id)
        leveled, level = await XPSystem.check_level_up(player)

        if leveled:
            await ctx.send(embed=success_embed(
                "LEVEL UP!",
                f"You are now Level {level}!"
            ))
        else:
            await ctx.send(embed=success_embed(
                "Training Complete",
                "You gained 50 XP."
            ))

async def setup(bot):
    await bot.add_cog(PlayerCommands(bot))
