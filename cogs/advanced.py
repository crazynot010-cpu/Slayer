import discord
import random
import time

from discord.ext import commands
from discord import app_commands

from database import users, guilds
from utils.calculations import calculate_shadow_power
from utils.rank_utils import get_rank_from_level


# ---------------- TRAITS ---------------- #

TRAITS = {
    "Brutal": 1.15,
    "Swift": 1.10,
    "Ancient": 1.20,
    "Cursed": 1.25,
    "Elite": 1.18
}

EVOLUTION_PATH = {
    "Common": "Rare",
    "Rare": "Epic",
    "Epic": "Legendary",
    "Legendary": "Mythic"
}

BOSS_BASE_HP = 5000
RAID_DURATION = 600  # 10 minutes


class AdvancedCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ==============================
    # TRAITS
    # ==============================

    def assign_trait(self):
        return random.choice(list(TRAITS.keys()))

    def trait_multiplier(self, trait):
        return TRAITS.get(trait, 1.0)

    # ==============================
    # EVOLUTION
    # ==============================

    async def evolve_shadow(self, user, shadow_name):
        for shadow in user["shadows"]:
            if shadow["name"].lower() == shadow_name.lower():
                if shadow["rarity"] not in EVOLUTION_PATH:
                    return "This shadow cannot evolve."

                if shadow["level"] < 5:
                    return "Shadow must be level 5 to evolve."

                shadow["rarity"] = EVOLUTION_PATH[shadow["rarity"]]
                shadow["level"] = 1
                shadow["base_power"] += 50

                await users.update_one(
                    {"_id": user["_id"]},
                    {"$set": {"shadows": user["shadows"]}}
                )

                return f"🌟 {shadow_name} evolved into {shadow['rarity']}!"
        return "Shadow not found."

    # ==============================
    # BOSS RAID
    # ==============================

    async def start_raid(self, guild_id):
        await guilds.update_one(
            {"guild_id": guild_id},
            {
                "$set": {
                    "raid": {
                        "hp": BOSS_BASE_HP,
                        "start_time": int(time.time()),
                        "participants": {}
                    }
                }
            }
        )

    async def attack_raid(self, member):
        guild_data = await guilds.find_one({"guild_id": member.guild.id})
        raid = guild_data.get("raid")

        if not raid:
            return "No active raid."

        if int(time.time()) - raid["start_time"] > RAID_DURATION:
            await guilds.update_one({"guild_id": member.guild.id}, {"$unset": {"raid": ""}})
            return "Raid expired."

        user = await users.find_one({
            "user_id": member.id,
            "guild_id": member.guild.id
        })

        if not user or not user["shadows"]:
            return "You need shadows to attack."

        total_power = sum(calculate_shadow_power(s) * self.trait_multiplier(s.get("trait")) for s in user["shadows"])
        damage = random.randint(int(total_power * 0.4), int(total_power * 0.7))

        raid["hp"] -= damage

        raid["participants"][str(member.id)] = raid["participants"].get(str(member.id), 0) + damage

        if raid["hp"] <= 0:
            winners = sorted(raid["participants"].items(), key=lambda x: x[1], reverse=True)
            top = winners[0][0]
            await guilds.update_one({"guild_id": member.guild.id}, {"$unset": {"raid": ""}})
            return f"🔥 Raid defeated! MVP: <@{top}>"

        await guilds.update_one(
            {"guild_id": member.guild.id},
            {"$set": {"raid": raid}}
        )

        return f"⚔️ You dealt {damage} damage! Boss HP left: {raid['hp']}"

    # ==============================
    # LEADERBOARD
    # ==============================

    async def leaderboard(self, guild_id):
        top = users.find({"guild_id": guild_id}).sort("level", -1).limit(10)

        text = "🏆 Leaderboard\n"
        rank = 1
        async for user in top:
            text += f"{rank}. <@{user['user_id']}> - Level {user['level']}\n"
            rank += 1

        return text

    # ==============================
    # COMMANDS
    # ==============================

    @commands.command(name="evolve")
    async def evolve_prefix(self, ctx, *, shadow_name: str):
        user = await users.find_one({"user_id": ctx.author.id, "guild_id": ctx.guild.id})
        result = await self.evolve_shadow(user, shadow_name)
        await ctx.send(result)

    @app_commands.command(name="evolve", description="Evolve a shadow")
    async def evolve_slash(self, interaction: discord.Interaction, shadow_name: str):
        user = await users.find_one({"user_id": interaction.user.id, "guild_id": interaction.guild.id})
        result = await self.evolve_shadow(user, shadow_name)
        await interaction.response.send_message(result)

    @commands.command(name="startraid")
    async def start_raid_prefix(self, ctx):
        await self.start_raid(ctx.guild.id)
        await ctx.send("🔥 Boss Raid Started!")

    @app_commands.command(name="startraid", description="Start a boss raid")
    async def start_raid_slash(self, interaction: discord.Interaction):
        await self.start_raid(interaction.guild.id)
        await interaction.response.send_message("🔥 Boss Raid Started!")

    @commands.command(name="raid")
    async def raid_prefix(self, ctx):
        result = await self.attack_raid(ctx.author)
        await ctx.send(result)

    @app_commands.command(name="raid", description="Attack the active raid boss")
    async def raid_slash(self, interaction: discord.Interaction):
        result = await self.attack_raid(interaction.user)
        await interaction.response.send_message(result)

    @commands.command(name="leaderboard")
    async def leaderboard_prefix(self, ctx):
        text = await self.leaderboard(ctx.guild.id)
        await ctx.send(text)

    @app_commands.command(name="leaderboard", description="Server leaderboard")
    async def leaderboard_slash(self, interaction: discord.Interaction):
        text = await self.leaderboard(interaction.guild.id)
        await interaction.response.send_message(text)


async def setup(bot):
    await bot.add_cog(AdvancedCog(bot))
