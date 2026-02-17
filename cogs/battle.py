import discord
import random
import time

from discord.ext import commands
from discord import app_commands

from database import users
from utils.calculations import calculate_shadow_power, xp_required
from utils.rank_utils import get_rank_from_level


BATTLE_COOLDOWN = 60
PVE_BASE_ENEMY = 120


class BattleCog(commands.Cog):
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
                "last_battle": 0,
                "wins": 0,
                "losses": 0,
                "shadows": []
            })

    def rank_multiplier(self, rank: str):
        multipliers = {
            "E": 1.0,
            "D": 1.1,
            "C": 1.2,
            "B": 1.3,
            "A": 1.4,
            "S": 1.5,
            "SS": 1.7,
            "SSS": 2.0
        }
        return multipliers.get(rank, 1.0)

    def total_power(self, user):
        total = 0
        for shadow in user["shadows"]:
            total += calculate_shadow_power(shadow)
        total *= self.rank_multiplier(user["rank"])
        return int(total)

    async def give_xp(self, user):
        xp_gain = random.randint(40, 70)
        new_xp = user["xp"] + xp_gain
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

        return xp_gain

    async def check_cooldown(self, user):
        now = int(time.time())
        if now - user.get("last_battle", 0) < BATTLE_COOLDOWN:
            remaining = BATTLE_COOLDOWN - (now - user.get("last_battle", 0))
            return False, remaining
        return True, 0

    async def update_cooldown(self, user):
        await users.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_battle": int(time.time())}}
        )

    async def pve_logic(self, member):
        await self.ensure_user(member.id, member.guild.id)
        user = await users.find_one({
            "user_id": member.id,
            "guild_id": member.guild.id
        })

        if not user["shadows"]:
            return "You need at least one shadow to battle."

        allowed, remaining = await self.check_cooldown(user)
        if not allowed:
            return f"Cooldown active. Try again in {remaining}s."

        player_power = self.total_power(user)
        enemy_power = PVE_BASE_ENEMY + random.randint(0, 150)

        await self.update_cooldown(user)

        if player_power >= enemy_power:
            xp = await self.give_xp(user)
            await users.update_one({"_id": user["_id"]}, {"$inc": {"wins": 1}})
            return f"⚔️ Victory!\nYour Power: {player_power}\nEnemy: {enemy_power}\n+{xp} XP"
        else:
            await users.update_one({"_id": user["_id"]}, {"$inc": {"losses": 1}})
            return f"💀 Defeat.\nYour Power: {player_power}\nEnemy: {enemy_power}"

    async def pvp_logic(self, challenger, opponent):
        await self.ensure_user(challenger.id, challenger.guild.id)
        await self.ensure_user(opponent.id, opponent.guild.id)

        user1 = await users.find_one({
            "user_id": challenger.id,
            "guild_id": challenger.guild.id
        })

        user2 = await users.find_one({
            "user_id": opponent.id,
            "guild_id": opponent.guild.id
        })

        if not user1["shadows"] or not user2["shadows"]:
            return "Both players need at least one shadow."

        allowed, remaining = await self.check_cooldown(user1)
        if not allowed:
            return f"Cooldown active. Try again in {remaining}s."

        power1 = self.total_power(user1)
        power2 = self.total_power(user2)

        await self.update_cooldown(user1)

        if power1 >= power2:
            xp = await self.give_xp(user1)
            await users.update_one({"_id": user1["_id"]}, {"$inc": {"wins": 1}})
            await users.update_one({"_id": user2["_id"]}, {"$inc": {"losses": 1}})
            return f"🔥 {challenger.mention} wins!\n{power1} vs {power2}\n+{xp} XP"
        else:
            await users.update_one({"_id": user1["_id"]}, {"$inc": {"losses": 1}})
            await users.update_one({"_id": user2["_id"]}, {"$inc": {"wins": 1}})
            return f"⚔️ {opponent.mention} wins!\n{power1} vs {power2}"

    # PREFIX
    @commands.command(name="battle")
    async def battle_prefix(self, ctx, mode: str, member: discord.Member = None):
        if mode.lower() == "pve":
            result = await self.pve_logic(ctx.author)
            await ctx.send(result)
        elif mode.lower() == "pvp" and member:
            result = await self.pvp_logic(ctx.author, member)
            await ctx.send(result)
        else:
            await ctx.send("Usage: !battle pve OR !battle pvp @user")

    # SLASH
    @app_commands.command(name="battle", description="Battle system")
    @app_commands.describe(mode="pve or pvp", opponent="Opponent for pvp")
    async def battle_slash(self, interaction: discord.Interaction, mode: str, opponent: discord.Member = None):
        if mode.lower() == "pve":
            result = await self.pve_logic(interaction.user)
            await interaction.response.send_message(result)
        elif mode.lower() == "pvp" and opponent:
            result = await self.pvp_logic(interaction.user, opponent)
            await interaction.response.send_message(result)
        else:
            await interaction.response.send_message("Usage: /battle mode:pve OR mode:pvp opponent:@user")


async def setup(bot):
    await bot.add_cog(BattleCog(bot))
