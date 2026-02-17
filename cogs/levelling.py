import discord
from discord.ext import commands
import time
import random
from core.database import users
from core.helpers import xp_needed, get_rank
from core.config import CHAT_COOLDOWN, XP_MIN, XP_MAX

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_user(self, user_id, guild_id):
        data = users.find_one({"user_id": user_id, "guild_id": guild_id})
        if not data:
            data = {
                "user_id": user_id,
                "guild_id": guild_id,
                "xp": 0,
                "level": 1,
                "rank": "E",
                "inventory": [],
                "background": None,
                "last_chat": 0
            }
            users.insert_one(data)
        return data

    async def handle_rank(self, member, level):
        new_rank = get_rank(level)
        role_name = f"{new_rank}-Rank"

        role = discord.utils.get(member.guild.roles, name=role_name)
        if not role:
            role = await member.guild.create_role(name=role_name)

        for r in member.roles:
            if r.name.endswith("-Rank"):
                await member.remove_roles(r)

        await member.add_roles(role)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        user = self.get_user(message.author.id, message.guild.id)
        now = time.time()

        if now - user["last_chat"] < CHAT_COOLDOWN:
            return

        gained = random.randint(XP_MIN, XP_MAX)
        user["xp"] += gained
        user["last_chat"] = now

        if user["xp"] >= xp_needed(user["level"]):
            user["xp"] = 0
            user["level"] += 1
            await self.handle_rank(message.author, user["level"])

        users.update_one(
            {"user_id": message.author.id, "guild_id": message.guild.id},
            {"$set": user}
        )

async def setup(bot):
    await bot.add_cog(Leveling(bot))
