import discord
from discord.ext import commands
from discord import app_commands
import random
import time
from config import SUCCESS_RATE, SHADOWS
from database.mongo import globals_db, users
from core.shadows import can_claim, add_shadow

class Spawn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def arise(self, ctx):
        data = await globals_db.find_one({"guild_id": ctx.guild.id})
        if not data or data["claimed"] or time.time() > data["expires_at"]:
            return await ctx.send("No active shadow.")

        user = await users.find_one({"user_id": ctx.author.id})

        allowed, reason = can_claim(user, data["shadow"])
        if not allowed:
            return await ctx.send(reason)

        user["attempts"] += 1

        if random.random() <= SUCCESS_RATE:
            user["successes"] += 1
            await add_shadow(user, data["shadow"], SHADOWS[data["shadow"]]["power"])
            await globals_db.update_one(
                {"guild_id": ctx.guild.id},
                {"$set": {"claimed": True}}
            )
            await ctx.send(f"🔥 {ctx.author.mention} arose {data['shadow']}!")
        else:
            await users.update_one({"user_id": ctx.author.id}, {"$set": user})
            await ctx.send("❌ Arise failed!")

async def setup(bot):
    await bot.add_cog(Spawn(bot))
