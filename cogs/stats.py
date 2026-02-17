import discord
from discord.ext import commands

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="stats")
    async def stats_prefix(self, ctx):
        total_users = await self.bot.db.users.count_documents({})
        embed = discord.Embed(title="Bot Stats", color=discord.Color.blue())
        embed.add_field(name="Registered Hunters", value=total_users)
        embed.add_field(name="Servers", value=len(self.bot.guilds))
        await ctx.send(embed=embed)

    @discord.app_commands.command(name="stats", description="View bot statistics")
    async def stats_slash(self, interaction: discord.Interaction):
        total_users = await self.bot.db.users.count_documents({})
        embed = discord.Embed(title="Bot Stats", color=discord.Color.blue())
        embed.add_field(name="Registered Hunters", value=total_users)
        embed.add_field(name="Servers", value=len(self.bot.guilds))
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Stats(bot))
