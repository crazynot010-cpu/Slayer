import discord
from discord.ext import commands
from discord import app_commands

from utils.embeds import base_embed


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # -------------------------
    # PREFIX HELP
    # -------------------------

    @commands.command(name="help")
    async def help_prefix(self, ctx):
        embed = self.build_help_embed(ctx.guild)
        await ctx.send(embed=embed)

    # -------------------------
    # SLASH HELP
    # -------------------------

    @app_commands.command(name="help", description="View all bot commands")
    async def help_slash(self, interaction: discord.Interaction):
        embed = self.build_help_embed(interaction.guild)
        await interaction.response.send_message(embed=embed)

    # -------------------------
    # EMBED BUILDER
    # -------------------------

    def build_help_embed(self, guild):
        embed = base_embed(title="📖 Bot Commands")

        embed.add_field(
            name="⚔️ Combat",
            value="""
`!attack` / `/attack`
`!forcespawn` (admin)
""",
            inline=False
        )

        embed.add_field(
            name="📈 Progression",
            value="""
`!profile` / `/profile`
`!leaderboard` / `/leaderboard`
""",
            inline=False
        )

        embed.add_field(
            name="💰 Economy",
            value="""
`!addgold` (admin)
`!addxp` (admin)
`!setlevel` (admin)
`!resetuser` (admin)
""",
            inline=False
        )

        embed.set_footer(text="Use / for slash commands or ! for prefix")

        return embed


async def setup(bot):
    await bot.add_cog(Help(bot))
