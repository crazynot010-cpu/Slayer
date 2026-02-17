import discord
import random
import asyncio
import time

from discord.ext import commands
from discord import app_commands

from database import guilds, shadows
from utils.spawn_manager import generate_spawn_threshold, spawn_chance
from utils.checks import admin_only


DESPAWN_TIME = 300  # 5 minutes


class SpawnCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spawn_tasks = {}

    async def ensure_guild(self, guild_id: int):
        existing = await guilds.find_one({"guild_id": guild_id})
        if not existing:
            await guilds.insert_one({
                "guild_id": guild_id,
                "spawn_channel": None,
                "xp_rate": 1.0,
                "message_count": 0,
                "next_spawn_threshold": generate_spawn_threshold(),
                "active_spawn": None
            })

    async def start_despawn_timer(self, guild_id: int):
        await asyncio.sleep(DESPAWN_TIME)

        guild_data = await guilds.find_one({"guild_id": guild_id})
        if not guild_data:
            return

        active = guild_data.get("active_spawn")
        if active:
            await guilds.update_one(
                {"guild_id": guild_id},
                {"$set": {"active_spawn": None}}
            )

            guild = self.bot.get_guild(guild_id)
            if guild and guild_data["spawn_channel"]:
                channel = guild.get_channel(guild_data["spawn_channel"])
                if channel:
                    await channel.send("⏳ The shadow has vanished...")

    async def spawn_shadow(self, guild: discord.Guild, shadow_name=None):
        await self.ensure_guild(guild.id)
        guild_data = await guilds.find_one({"guild_id": guild.id})

        if guild_data["active_spawn"]:
            return None

        if not shadow_name:
            all_shadows = await shadows.find().to_list(length=None)
            if not all_shadows:
                return None
            shadow = random.choice(all_shadows)
        else:
            shadow = await shadows.find_one({"name": shadow_name})
            if not shadow:
                return None

        spawn_data = {
            "name": shadow["name"],
            "rarity": shadow["rarity"],
            "base_power": shadow["base_power"],
            "started_at": time.time(),
            "claimed_by": None
        }

        await guilds.update_one(
            {"guild_id": guild.id},
            {"$set": {"active_spawn": spawn_data}}
        )

        if guild_data["spawn_channel"]:
            channel = guild.get_channel(guild_data["spawn_channel"])
        else:
            channel = guild.system_channel

        if channel:
            embed = discord.Embed(
                title="⚔ A Shadow Has Appeared!",
                description=f"**{shadow['name']}**\nRarity: {shadow['rarity']}",
                color=0x8e44ad
            )
            await channel.send(embed=embed)

        task = asyncio.create_task(self.start_despawn_timer(guild.id))
        self.spawn_tasks[guild.id] = task

        return True

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        await self.ensure_guild(message.guild.id)

        guild_data = await guilds.find_one({"guild_id": message.guild.id})

        if guild_data["active_spawn"]:
            return

        new_count = guild_data["message_count"] + 1

        if new_count >= guild_data["next_spawn_threshold"]:
            if spawn_chance():
                await self.spawn_shadow(message.guild)

            await guilds.update_one(
                {"guild_id": message.guild.id},
                {
                    "$set": {
                        "message_count": 0,
                        "next_spawn_threshold": generate_spawn_threshold()
                    }
                }
            )
        else:
            await guilds.update_one(
                {"guild_id": message.guild.id},
                {"$set": {"message_count": new_count}}
            )

    @commands.command(name="spawn")
    async def spawn_prefix(self, ctx):
        result = await self.spawn_shadow(ctx.guild)
        if not result:
            await ctx.send("A shadow is already active or none exist.")

    @app_commands.command(name="spawn", description="Spawn a shadow manually")
    async def spawn_slash(self, interaction: discord.Interaction):
        result = await self.spawn_shadow(interaction.guild)
        if not result:
            await interaction.response.send_message(
                "A shadow is already active or none exist."
            )
        else:
            await interaction.response.send_message("Shadow spawned.")

    @commands.command(name="despawn")
    @admin_only()
    async def despawn_prefix(self, ctx):
        await guilds.update_one(
            {"guild_id": ctx.guild.id},
            {"$set": {"active_spawn": None}}
        )
        await ctx.send("Active shadow despawned.")

    @app_commands.command(name="despawn", description="Force despawn")
    async def despawn_slash(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Admin only.")
            return

        await guilds.update_one(
            {"guild_id": interaction.guild.id},
            {"$set": {"active_spawn": None}}
        )
        await interaction.response.send_message("Active shadow despawned.")

    @commands.command(name="setspawn")
    @admin_only()
    async def setspawn_prefix(self, ctx, channel: discord.TextChannel):
        await guilds.update_one(
            {"guild_id": ctx.guild.id},
            {"$set": {"spawn_channel": channel.id}}
        )
        await ctx.send(f"Spawn channel set to {channel.mention}")

    @app_commands.command(name="setspawnchannel", description="Set spawn channel")
    async def setspawn_slash(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Admin only.")
            return

        await guilds.update_one(
            {"guild_id": interaction.guild.id},
            {"$set": {"spawn_channel": channel.id}}
        )

        await interaction.response.send_message(
            f"Spawn channel set to {channel.mention}"
        )


async def setup(bot):
    await bot.add_cog(SpawnCog(bot))
