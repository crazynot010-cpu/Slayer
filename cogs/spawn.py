import discord
from discord.ext import commands
import random
import asyncio
import time
from core.database import guilds, users, shadows
from core.config import *
from core.helpers import xp_needed

class Spawn(commands.Cog):
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

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        guild_data = self.get_guild(message.guild.id)
        guild_data["message_count"] += 1

        guilds.update_one(
            {"guild_id": message.guild.id},
            {"$set": {"message_count": guild_data["message_count"]}}
        )

        if guild_data["message_count"] >= random.randint(SPAWN_TRIGGER_MIN, SPAWN_TRIGGER_MAX):
            guilds.update_one(
                {"guild_id": message.guild.id},
                {"$set": {"message_count": 0}}
            )

            if random.random() <= SPAWN_CHANCE:
                await self.spawn_shadow(message.guild)

    async def spawn_shadow(self, guild):
        guild_data = self.get_guild(guild.id)

        if guild_data["active_spawn"]:
            return

        shadow_list = list(shadows.find())
        if not shadow_list:
            return

        chosen = random.choice(shadow_list)

        guilds.update_one(
            {"guild_id": guild.id},
            {"$set": {
                "active_spawn": {
                    "name": chosen["name"],
                    "image": chosen["image"],
                    "expires": time.time() + SPAWN_TIMEOUT,
                    "claimed": False
                }
            }}
        )

        channel = guild.get_channel(guild_data["spawn_channel"]) if guild_data["spawn_channel"] else guild.system_channel
        role_ping = f"<@&{guild_data['ping_role']}>" if guild_data["ping_role"] else ""

        embed = discord.Embed(
            title="A Shadow Has Appeared!",
            description="Use `/arise` or `!arise` to capture it!",
            color=discord.Color.dark_purple()
        )
        embed.set_image(url=chosen["image"])

        await channel.send(content=role_ping, embed=embed)

        await asyncio.sleep(SPAWN_TIMEOUT)

        guild_data = self.get_guild(guild.id)
        if guild_data["active_spawn"] and not guild_data["active_spawn"]["claimed"]:
            guilds.update_one(
                {"guild_id": guild.id},
                {"$set": {"active_spawn": None}}
            )
            await channel.send("The shadow vanished...")

    @commands.command()
    async def arise(self, ctx):
        guild_data = self.get_guild(ctx.guild.id)
        spawn = guild_data["active_spawn"]

        if not spawn:
            return await ctx.send("No active shadow.")

        if spawn["claimed"]:
            return await ctx.send("Already claimed.")

        if time.time() > spawn["expires"]:
            guilds.update_one({"guild_id": ctx.guild.id}, {"$set": {"active_spawn": None}})
            return await ctx.send("Shadow expired.")

        user = users.find_one({"user_id": ctx.author.id, "guild_id": ctx.guild.id})
        if not user:
            return

        total = sum(i["count"] for i in user["inventory"])
        if total >= MAX_SLOTS:
            return await ctx.send("Inventory full.")

        existing = next((i for i in user["inventory"] if i["name"] == spawn["name"]), None)
        if existing and existing["count"] >= MAX_DUPE:
            return await ctx.send("Max duplicate reached.")

        if random.random() <= ARISE_SUCCESS:
            if existing:
                existing["count"] += 1
            else:
                user["inventory"].append({"name": spawn["name"], "count": 1})

            user["xp"] += ARISE_XP_BONUS
            users.update_one(
                {"user_id": ctx.author.id, "guild_id": ctx.guild.id},
                {"$set": user}
            )

            guilds.update_one(
                {"guild_id": ctx.guild.id},
                {"$set": {"active_spawn": None}}
            )

            await ctx.send(f"Success! You obtained {spawn['name']} (+{ARISE_XP_BONUS} XP)")

        else:
            await ctx.send("You failed to arise it!")

async def setup(bot):
    await bot.add_cog(Spawn(bot))
