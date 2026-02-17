import discord
import random

from discord.ext import commands
from discord import app_commands

from database import guilds, users
from utils.calculations import xp_required
from utils.rank_utils import get_rank_from_level


BASE_SUCCESS_RATE = 0.55
MAX_SLOTS = 16
MAX_DUPES = 3
SUCCESS_XP_REWARD = 50


class AriseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def ensure_user(self, user_id: int, guild_id: int):
        user = await users.find_one({"user_id": user_id, "guild_id": guild_id})
        if not user:
            await users.insert_one({
                "user_id": user_id,
                "guild_id": guild_id,
                "xp": 0,
                "level": 1,
                "rank": "E",
                "last_xp_time": 0,
                "shadows": [],
                "attempts": 0,
                "successes": 0
            })

    async def attempt_arise(self, member: discord.Member):
        guild_id = member.guild.id

        guild_data = await guilds.find_one({"guild_id": guild_id})
        if not guild_data:
            return "No active shadow.", False

        active = guild_data.get("active_spawn")
        if not active:
            return "No active shadow.", False

        if active.get("claimed_by"):
            return "This shadow has already been claimed.", False

        await self.ensure_user(member.id, guild_id)

        user = await users.find_one({
            "user_id": member.id,
            "guild_id": guild_id
        })

        inventory = user.get("shadows", [])

        # Slot limit
        if len(inventory) >= MAX_SLOTS:
            return "You have reached the max shadow slots (16).", False

        # Duplicate limit
        dupes = sum(1 for s in inventory if s["name"] == active["name"])
        if dupes >= MAX_DUPES:
            return "You already own 3 duplicates of this shadow.", False

        success = random.random() <= BASE_SUCCESS_RATE

        await users.update_one(
            {"_id": user["_id"]},
            {"$inc": {"attempts": 1}}
        )

        if not success:
            return "❌ Arise failed. You may try again before despawn.", False

        # 🔒 Atomic claim
        result = await guilds.update_one(
            {
                "guild_id": guild_id,
                "active_spawn.claimed_by": None
            },
            {
                "$set": {"active_spawn.claimed_by": member.id}
            }
        )

        if result.modified_count == 0:
            return "Too late. Someone else claimed it.", False

        # Add shadow to inventory
        new_shadow = {
            "name": active["name"],
            "rarity": active["rarity"],
            "base_power": active["base_power"],
            "level": 1,
            "trait": None
        }

        await users.update_one(
            {"_id": user["_id"]},
            {
                "$push": {"shadows": new_shadow},
                "$inc": {"successes": 1}
            }
        )

        # XP logic
        new_xp = user["xp"] + SUCCESS_XP_REWARD
        level = user["level"]

        while new_xp >= xp_required(level):
            new_xp -= xp_required(level)
            level += 1

        new_rank = get_rank_from_level(level)

        await users.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "xp": new_xp,
                    "level": level,
                    "rank": new_rank
                }
            }
        )

        # ✅ CLEAR ACTIVE SPAWN AFTER SUCCESS
        await guilds.update_one(
            {"guild_id": guild_id},
            {"$set": {"active_spawn": None}}
        )

        return f"🔥 SUCCESS! **{active['name']}** has joined your army!", True

    

    @app_commands.command(name="arise", description="Attempt to claim active shadow")
async def arise_slash(self, interaction: discord.Interaction):
    message, success = await self.attempt_arise(interaction.user)

    if not interaction.response.is_done():
        await interaction.response.send_message(message)
    else:
        await interaction.followup.send(message) 
        

async def setup(bot):
    await bot.add_cog(AriseCog(bot))
