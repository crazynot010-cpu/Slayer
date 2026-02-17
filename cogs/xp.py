import discord
import random
import time
from discord.ext import commands
from discord import app_commands

from database import users, guilds
from utils.calculations import xp_required
from utils.rank_utils import get_rank_from_level, RANK_COLORS

XP_COOLDOWN = 15  # seconds
XP_MIN = 8
XP_MAX = 15


class XPCog(commands.Cog):
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

    async def handle_rank_update(self, member: discord.Member, new_rank: str):
        guild = member.guild
        role_name = f"Hunter {new_rank}"

        role = discord.utils.get(guild.roles, name=role_name)

        if not role:
            role = await guild.create_role(
                name=role_name,
                colour=discord.Colour(RANK_COLORS[new_rank])
            )

        # Remove old hunter roles
        for r in member.roles:
            if r.name.startswith("Hunter ") and r.name != role_name:
                await member.remove_roles(r)

        if role not in member.roles:
            await member.add_roles(role)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        await self.ensure_user(message.author.id, message.guild.id)

        user = await users.find_one({
            "user_id": message.author.id,
            "guild_id": message.guild.id
        })

        now = time.time()
        if now - user["last_xp_time"] < XP_COOLDOWN:
            return

        # Safe guild config
        guild_config = await guilds.find_one({"guild_id": message.guild.id}) or {}
        xp_rate = guild_config.get("xp_rate", 1.0)

        gained = int(random.randint(XP_MIN, XP_MAX) * xp_rate)

        new_xp = user["xp"] + gained
        level = user["level"]
        leveled_up = False

        while new_xp >= xp_required(level):
            new_xp -= xp_required(level)
            level += 1
            leveled_up = True

        new_rank = get_rank_from_level(level)

        await users.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "xp": new_xp,
                    "level": level,
                    "rank": new_rank,
                    "last_xp_time": now
                }
            }
        )

        if leveled_up:
            await message.channel.send(
                f"🎉 {message.author.mention} leveled up to **Level {level}**!"
            )
            await self.handle_rank_update(message.author, new_rank)

    # ---------------- COMMANDS ---------------- #

    @commands.command(name="xp")
    async def xp_prefix(self, ctx):
        await self.ensure_user(ctx.author.id, ctx.guild.id)
        user = await users.find_one({
            "user_id": ctx.author.id,
            "guild_id": ctx.guild.id
        })

        await ctx.send(
            f"XP: {user['xp']} / {xp_required(user['level'])}"
        )

    @app_commands.command(name="xp", description="View your XP")
    async def xp_slash(self, interaction: discord.Interaction):
        await self.ensure_user(interaction.user.id, interaction.guild.id)
        user = await users.find_one({
            "user_id": interaction.user.id,
            "guild_id": interaction.guild.id
        })

        await interaction.response.send_message(
            f"XP: {user['xp']} / {xp_required(user['level'])}"
        )

    @commands.command(name="level")
    async def level_prefix(self, ctx):
        await self.ensure_user(ctx.author.id, ctx.guild.id)
        user = await users.find_one({
            "user_id": ctx.author.id,
            "guild_id": ctx.guild.id
        })

        await ctx.send(
            f"Level: {user['level']} | Rank: {user['rank']}"
        )

    @app_commands.command(name="level", description="View your level info")
    async def level_slash(self, interaction: discord.Interaction):
        await self.ensure_user(interaction.user.id, interaction.guild.id)
        user = await users.find_one({
            "user_id": interaction.user.id,
            "guild_id": interaction.guild.id
        })

        await interaction.response.send_message(
            f"Level: {user['level']} | Rank: {user['rank']}"
        )


async def setup(bot):
    await bot.add_cog(XPCog(bot))
