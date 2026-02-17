import discord
from discord.ext import commands
from discord import app_commands
from core.database import guilds, shadows
from core.config import SPAWN_TIMEOUT
import random
import time

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =============================
    # SET SPAWN CHANNEL
    # =============================

    @app_commands.command(name="setchannelspawn")
    @app_commands.checks.has_permissions(administrator=True)
    async def setchannelspawn_slash(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.defer(ephemeral=True)

        guilds.update_one(
            {"guild_id": interaction.guild.id},
            {"$set": {"spawn_channel": channel.id}},
            upsert=True
        )

        await interaction.followup.send("Spawn channel set.", ephemeral=True)

    @commands.command(name="setchannelspawn")
    @commands.has_permissions(administrator=True)
    async def setchannelspawn_prefix(self, ctx, channel: discord.TextChannel):
        guilds.update_one(
            {"guild_id": ctx.guild.id},
            {"$set": {"spawn_channel": channel.id}},
            upsert=True
        )
        await ctx.send("Spawn channel set.")

    # =============================
    # SET PING ROLE
    # =============================

    @app_commands.command(name="setpingrole")
    @app_commands.checks.has_permissions(administrator=True)
    async def setpingrole_slash(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.defer(ephemeral=True)

        guilds.update_one(
            {"guild_id": interaction.guild.id},
            {"$set": {"ping_role": role.id}},
            upsert=True
        )

        await interaction.followup.send("Ping role set.", ephemeral=True)

    @commands.command(name="setpingrole")
    @commands.has_permissions(administrator=True)
    async def setpingrole_prefix(self, ctx, role: discord.Role):
        guilds.update_one(
            {"guild_id": ctx.guild.id},
            {"$set": {"ping_role": role.id}},
            upsert=True
        )
        await ctx.send("Ping role set.")

    # =============================
    # MANUAL SPAWN
    # =============================

    @app_commands.command(name="spawnshadow")
    @app_commands.checks.has_permissions(administrator=True)
    async def spawnshadow_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()

        shadow_list = list(shadows.find())
        if not shadow_list:
            return await interaction.followup.send("No shadows available.")

        chosen = random.choice(shadow_list)

        guilds.update_one(
            {"guild_id": interaction.guild.id},
            {"$set": {
                "active_spawn": {
                    "name": chosen["name"],
                    "image": chosen["image"],
                    "expires": time.time() + SPAWN_TIMEOUT,
                    "claimed": False
                }
            }},
            upsert=True
        )

        embed = discord.Embed(
            title="Shadow Spawned!",
            description="Use `/arise` or `!arise`",
            color=discord.Color.dark_purple()
        )
        embed.set_image(url=chosen["image"])

        await interaction.followup.send(embed=embed)

    @commands.command(name="spawnshadow")
    @commands.has_permissions(administrator=True)
    async def spawnshadow_prefix(self, ctx):
        shadow_list = list(shadows.find())
        if not shadow_list:
            return await ctx.send("No shadows available.")

        chosen = random.choice(shadow_list)

        guilds.update_one(
            {"guild_id": ctx.guild.id},
            {"$set": {
                "active_spawn": {
                    "name": chosen["name"],
                    "image": chosen["image"],
                    "expires": time.time() + SPAWN_TIMEOUT,
                    "claimed": False
                }
            }},
            upsert=True
        )

        embed = discord.Embed(
            title="Shadow Spawned!",
            description="Use `/arise` or `!arise`",
            color=discord.Color.dark_purple()
        )
        embed.set_image(url=chosen["image"])

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Admin(bot))
