import discord
from discord.ext import commands
from discord import app_commands

from database import users


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def ensure_user(self, user_id: int, guild_id: int):
        user = await users.find_one({"user_id": user_id, "guild_id": guild_id})
        if not user:
            await users.insert_one({
                "user_id": user_id,
                "guild_id": guild_id,
                "xp": 0,
                "level": 1,
                "rank": "E",
                "last_xp_time": 0,
                "shadows": [],
                "attempts": 0,
                "successes": 0
            })

    async def send_profile(self, ctx, member, slash=False):
        await self.ensure_user(member.id, member.guild.id)

        user = await users.find_one({
            "user_id": member.id,
            "guild_id": member.guild.id
        })

        embed = discord.Embed(
            title=f"{member.name}'s Hunter Profile",
            color=discord.Color.dark_purple()
        )

        embed.add_field(name="Level", value=user["level"], inline=True)
        embed.add_field(name="XP", value=user["xp"], inline=True)
        embed.add_field(name="Rank", value=user["rank"], inline=True)
        embed.add_field(name="Shadows Owned", value=len(user.get("shadows", [])), inline=True)
        embed.add_field(name="Attempts", value=user.get("attempts", 0), inline=True)
        embed.add_field(name="Successes", value=user.get("successes", 0), inline=True)

        embed.set_thumbnail(url=member.display_avatar.url)

        if slash:
            await ctx.response.send_message(embed=embed)
        else:
            await ctx.send(embed=embed)

    # -------- Commands -------- #

    @commands.command(name="profile")
    async def profile_prefix(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        await self.send_profile(ctx, member)

    @app_commands.command(name="profile", description="View hunter profile")
    async def profile_slash(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        await self.send_profile(interaction, member, slash=True)


async def setup(bot):
    await bot.add_cog(Profile(bot))
