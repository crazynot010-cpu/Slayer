import discord
from discord.ext import commands

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def build_leaderboard(self):
        users = self.bot.db.users.find().sort("level", -1).limit(10)
        result = []
        async for user in users:
            result.append(user)
        return result

    @commands.command(name="leaderboard")
    async def leaderboard_prefix(self, ctx):
        await self.send_lb(ctx)

    @discord.app_commands.command(name="leaderboard", description="Top hunters")
    async def leaderboard_slash(self, interaction: discord.Interaction):
        await self.send_lb(interaction, slash=True)

    async def send_lb(self, ctx, slash=False):
        data = await self.build_leaderboard()

        embed = discord.Embed(
            title="🏆 Top Hunters",
            color=discord.Color.gold()
        )

        for i, user in enumerate(data, start=1):
            embed.add_field(
                name=f"#{i}",
                value=f"<@{user['_id']}> — Level {user.get('level',1)}",
                inline=False
            )

        if slash:
            await ctx.response.send_message(embed=embed)
        else:
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
