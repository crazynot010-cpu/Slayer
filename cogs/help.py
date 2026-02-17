import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_prefix(self, ctx):
        await self.send_help(ctx)

    @discord.app_commands.command(name="help", description="Show help menu")
    async def help_slash(self, interaction: discord.Interaction):
        await self.send_help(interaction, slash=True)

    async def send_help(self, ctx, slash=False):
        embed = discord.Embed(
            title="Shadow Bot Commands",
            color=discord.Color.dark_theme()
        )

        embed.add_field(name="Profile", value="!profile", inline=False)
        embed.add_field(name="Leaderboard", value="!leaderboard", inline=False)
        embed.add_field(name="Inventory", value="!inventory", inline=False)
        embed.add_field(name="Arise", value="!arise", inline=False)

        if slash:
            await ctx.response.send_message(embed=embed)
        else:
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Help(bot))
