import discord
from discord import app_commands
from discord.ext import commands

from database import users_collection


class Leaderboard(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="leaderboard",
        description="View the top hunters in this server"
    )
    async def leaderboard(self, interaction: discord.Interaction):

        users = await users_collection.find(
            {"guild_id": interaction.guild.id}
        ).to_list(length=None)

        if not users:
            await interaction.response.send_message(
                "No data yet."
            )
            return

        # Sort by level first, then XP
        users_sorted = sorted(
            users,
            key=lambda u: (u["level"], u["xp"]),
            reverse=True
        )

        top_users = users_sorted[:10]

        embed = discord.Embed(
            title="🏆 Hunter Leaderboard",
            color=0x2f3136
        )

        description = ""

        for index, user in enumerate(top_users, start=1):
            member = interaction.guild.get_member(user["user_id"])

            name = member.display_name if member else "Unknown"

            description += (
                f"**{index}. {name}** "
                f"- Level {user['level']} "
                f"({user['xp']} XP)\n"
            )

        embed.description = description

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
