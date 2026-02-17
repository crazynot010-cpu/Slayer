import discord
from discord.ext import commands
import random
from database.mongo import users, guilds
from core.xp import handle_xp
from core.spawn import create_spawn

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        user = await users.find_one({"user_id": message.author.id})
        if not user:
            user = {
                "user_id": message.author.id,
                "xp": 0,
                "level": 1,
                "rank": "E",
                "shadows": [],
                "total_power": 0,
                "attempts": 0,
                "successes": 0,
                "last_xp": 0
            }
            await users.insert_one(user)

        leveled = await handle_xp(user)

        guild_data = await guilds.find_one({"guild_id": message.guild.id})
        if not guild_data:
            guild_data = {
                "guild_id": message.guild.id,
                "message_count": 0,
                "spawn_threshold": random.randint(30, 60),
                "rank_roles": {}
            }
            await guilds.insert_one(guild_data)

        guild_data["message_count"] += 1

        if guild_data["message_count"] >= guild_data["spawn_threshold"]:
            guild_data["message_count"] = 0
            guild_data["spawn_threshold"] = random.randint(30, 60)
            shadow = await create_spawn(message.guild.id)
            await message.channel.send(f"⚔ {shadow} has appeared!")

        await guilds.update_one(
            {"guild_id": message.guild.id},
            {"$set": guild_data}
        )

        await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(Events(bot))
