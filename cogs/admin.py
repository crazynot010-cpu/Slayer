import discord
from discord.ext import commands
from discord import app_commands
from core.database import guilds
from core.config import SPAWN_TIMEOUT
import random
import time
from core.database import shadows

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_guild(self, guild_id):
        data = guilds.find_one({"guild_id": guild_id})
        if not data:
            data = {
                "guild_id": guild_id,
                "message_count": 0,
                "active_spawn": None,
                "spawn_channel": None,
                "ping_role": None
            }
            guilds.insert_one(data)
        return data

    @app_commands.command(name="setchannelspawn")
    @app_commands.checks.has_permissions(administrator=True)
    async def setchannelspawn(self, interaction: discord.Interaction, channel: discord.TextChannel):
        guilds.update_one(
            {"guild_id": interaction.guild.id},
            {"$set": {"spawn_channel": channel.id}},
            upsert=True
        )
        await interaction.response.send_message("Spawn channel set.")

    @app_commands.command(name="setpingrole")
    @app_commands.checks.has_permissions(administrator=True)
    async def setpingrole(self, interaction: discord.Interaction, role: discord.Role):
        guilds.update_one(
            {"guild_id": interaction.guild.id},
            {"$set": {"ping_role": role.id}},
            upsert=True
        )
        await interaction.response.send_message("Ping role set.")

    @app_commands.command(name="spawnshadow")
    @app_commands.checks.has_permissions(administrator=True)
    async def spawnshadow(self, interaction: discord.Interaction):
        shadow_list = list(shadows.find())
        if not shadow_list:
            return await interaction.response.send_message("No shadows available.")

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
            }}
        )

        embed = discord.Embed(
            title="Shadow Spawned!",
            description="Use `/arise` or `!arise`",
            color=discord.Color.dark_purple()
        )
        embed.set_image(url=chosen["image"])

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Admin(bot))
