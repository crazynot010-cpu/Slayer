import discord
from discord import app_commands
from discord.ext import commands

from models.user_model import UserModel
from systems.xp_system import XPSystem


class Profile(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ---------------- PROFILE ----------------

    @app_commands.command(
        name="profile",
        description="View hunter profile"
    )
    async def profile(
        self,
        interaction: discord.Interaction,
        member: discord.Member = None
    ):
        member = member or interaction.user

        user = await UserModel.get_user(
            member.id,
            interaction.guild.id
        )

        xp_needed = XPSystem.xp_needed(user["level"])
        shadow_count = len(user["shadows"])

        embed = discord.Embed(color=0x2f3136)

        embed.set_author(
            name=f"{member.display_name}'s Hunter Profile",
            icon_url=member.display_avatar.url
        )

        embed.add_field(name="Level", value=user["level"], inline=True)
        embed.add_field(
            name="XP",
            value=f"{user['xp']} / {xp_needed}",
            inline=True
        )
        embed.add_field(name="Shadows", value=shadow_count, inline=True)

        # Background priority
        bg = user.get("background_global")

        if not bg:
            bg = user.get("background_guilds", {}).get(
                str(interaction.guild.id)
            )

        if bg:
            embed.set_image(url=bg)

        await interaction.response.send_message(embed=embed)

    # ---------------- USER BACKGROUND ----------------

    @app_commands.command(
        name="background",
        description="Set your profile background (guild only)"
    )
    async def background(
        self,
        interaction: discord.Interaction,
        url: str
    ):
        if not url.startswith(("http://", "https://")):
            await interaction.response.send_message(
                "❌ Invalid URL.",
                ephemeral=True
            )
            return

        user = await UserModel.get_user(
            interaction.user.id,
            interaction.guild.id
        )

        guild_bgs = user.get("background_guilds", {})
        guild_bgs[str(interaction.guild.id)] = url

        await UserModel.update_user(
            interaction.user.id,
            interaction.guild.id,
            {"background_guilds": guild_bgs}
        )

        await interaction.response.send_message(
            "✅ Guild background updated!"
        )

    # ---------------- ADMIN BACKGROUND ----------------

    @app_commands.command(
        name="setbackground",
        description="Admin: set background (global or guild)"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setbackground(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        url: str,
        global_mode: bool
    ):
        if not url.startswith(("http://", "https://")):
            await interaction.response.send_message(
                "❌ Invalid URL.",
                ephemeral=True
            )
            return

        if global_mode:
            await UserModel.update_user(
                member.id,
                interaction.guild.id,
                {"background_global": url}
            )

            await interaction.response.send_message(
                f"🌍 Global background set for {member.mention}"
            )

        else:
            user = await UserModel.get_user(
                member.id,
                interaction.guild.id
            )

            guild_bgs = user.get("background_guilds", {})
            guild_bgs[str(interaction.guild.id)] = url

            await UserModel.update_user(
                member.id,
                interaction.guild.id,
                {"background_guilds": guild_bgs}
            )

            await interaction.response.send_message(
                f"🏠 Guild background set for {member.mention}"
            )


async def setup(bot):
    await bot.add_cog(Profile(bot))
