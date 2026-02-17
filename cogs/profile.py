import discord
from discord.ext import commands

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_profile_data(self, user_id: int):
        return await self.bot.db.users.find_one({"_id": user_id})

    @commands.command(name="profile")
    async def profile_prefix(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        await self.send_profile(ctx, member)

    @discord.app_commands.command(name="profile", description="View your hunter profile")
    async def profile_slash(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        await self.send_profile(interaction, member, slash=True)

    async def send_profile(self, ctx, member, slash=False):
        data = await self.get_profile_data(member.id)

        if not data:
            msg = "No data found for this user."
            if slash:
                return await ctx.response.send_message(msg)
            return await ctx.send(msg)

        embed = discord.Embed(
            title=f"{member.name}'s Hunter Profile",
            color=discord.Color.dark_purple()
        )

        embed.add_field(name="Level", value=data.get("level", 1))
        embed.add_field(name="XP", value=data.get("xp", 0))
        embed.add_field(name="Rank", value=data.get("rank", "E"))
        embed.add_field(name="Shadows", value=len(data.get("shadows", [])))
        embed.set_thumbnail(url=member.display_avatar.url)

        if slash:
            await ctx.response.send_message(embed=embed)
        else:
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Profile(bot))
