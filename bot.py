import discord
from discord.ext import commands
from discord import app_commands
import random
import math
import os
import time
from pymongo import MongoClient

# =============================
# CONFIG
# =============================

TOKEN = os.getenv("TOKEN")
MONGO_URI = os.getenv("MONGO_URL")

XP_COOLDOWN = 60  # seconds

# =============================
# BOT SETUP (PATCHED HELP)
# =============================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix=".",
    intents=intents,
    help_command=None  # IMPORTANT PATCH
)

# =============================
# DATABASE
# =============================

mongo = MongoClient(MONGO_URI)
db = mongo["LevelSystem"]
levels = db["Levels"]
settings = db["Settings"]

# =============================
# XP FORMULA
# =============================

def xp_for_next(level):
    return 5 * (level ** 2) + 50 * level + 100

def create_bar(current, required, size=20):
    filled = int(size * current / required)
    return "█" * filled + "░" * (size - filled)

# =============================
# READY EVENT
# =============================

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Slash commands synced: {len(synced)}")
    except Exception as e:
        print(e)

    print(f"Logged in as {bot.user}")

# =============================
# MESSAGE XP SYSTEM (WEIGHTED)
# =============================

cooldowns = {}

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = str(message.author.id)
    guild_id = str(message.guild.id)

    key = f"{guild_id}-{user_id}"

    now = time.time()
    if key in cooldowns and now - cooldowns[key] < XP_COOLDOWN:
        await bot.process_commands(message)
        return

    cooldowns[key] = now

    data = levels.find_one({"guild_id": guild_id, "user_id": user_id})

    if not data:
        levels.insert_one({
            "guild_id": guild_id,
            "user_id": user_id,
            "xp": 0,
            "level": 0
        })
        data = levels.find_one({"guild_id": guild_id, "user_id": user_id})

    base_xp = random.randint(10, 20)

    # Weighted XP (longer messages = more XP)
    bonus = min(len(message.content) // 20, 15)
    gained = base_xp + bonus

    new_xp = data["xp"] + gained
    current_level = data["level"]

    required = xp_for_next(current_level)

    if new_xp >= required:
        new_xp -= required
        current_level += 1

        levels.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$set": {"xp": new_xp, "level": current_level}}
        )

        guild_settings = settings.find_one({"guild_id": guild_id})
        channel = message.channel

        if guild_settings and guild_settings.get("levelup_channel"):
            channel = bot.get_channel(guild_settings["levelup_channel"])

        ping_role = None
        if guild_settings and guild_settings.get("ping_role"):
            role = message.guild.get_role(guild_settings["ping_role"])
            if role:
                ping_role = role.mention

        await channel.send(
            f"{message.author.mention} leveled up to **Level {current_level}!** 🎉"
            + (f"\n{ping_role}" if ping_role else "")
        )

    else:
        levels.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$set": {"xp": new_xp}}
        )

    await bot.process_commands(message)

# =============================
# PREFIX COMMANDS
# =============================

@bot.command()
async def rank(ctx, member: discord.Member = None):
    member = member or ctx.author
    guild_id = str(ctx.guild.id)

    data = levels.find_one({"guild_id": guild_id, "user_id": str(member.id)})

    if not data:
        return await ctx.send("No XP yet.")

    level = data["level"]
    xp = data["xp"]
    required = xp_for_next(level)

    percent = round((xp / required) * 100, 1)
    bar = create_bar(xp, required)

    embed = discord.Embed(
        title=f"{member.name}'s Rank",
        color=discord.Color.blue()
    )

    embed.add_field(name="Level", value=level)
    embed.add_field(name="XP", value=f"{xp}/{required} ({percent}%)", inline=False)
    embed.add_field(name="Progress", value=bar, inline=False)

    await ctx.send(embed=embed)

@bot.command()
async def leaderboard(ctx):
    guild_id = str(ctx.guild.id)
    top = levels.find({"guild_id": guild_id}).sort("level", -1).limit(10)

    desc = ""
    for i, user in enumerate(top, start=1):
        member = ctx.guild.get_member(int(user["user_id"]))
        name = member.name if member else "Unknown"
        desc += f"**{i}. {name}** - Level {user['level']}\n"

    embed = discord.Embed(
        title="Leaderboard",
        description=desc,
        color=discord.Color.gold()
    )

    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def setlevelup(ctx, channel: discord.TextChannel):
    settings.update_one(
        {"guild_id": str(ctx.guild.id)},
        {"$set": {"levelup_channel": channel.id}},
        upsert=True
    )
    await ctx.send("Level-up channel set.")

@bot.command()
@commands.has_permissions(administrator=True)
async def setpingrole(ctx, role: discord.Role):
    settings.update_one(
        {"guild_id": str(ctx.guild.id)},
        {"$set": {"ping_role": role.id}},
        upsert=True
    )
    await ctx.send("Ping role set.")

@bot.command()
@commands.has_permissions(administrator=True)
async def setxp(ctx, member: discord.Member, xp: int):
    levels.update_one(
        {"guild_id": str(ctx.guild.id), "user_id": str(member.id)},
        {"$set": {"xp": xp}},
        upsert=True
    )
    await ctx.send("XP updated.")

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="Help",
        description="""
!rank
!leaderboard
!setlevelup
!setpingrole
!setxp
        """,
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

# =============================
# SLASH COMMANDS
# =============================

@bot.tree.command(name="rank", description="View your rank")
async def slash_rank(interaction: discord.Interaction):
    guild_id = str(interaction.guild.id)
    user_id = str(interaction.user.id)

    data = levels.find_one({"guild_id": guild_id, "user_id": user_id})

    if not data:
        return await interaction.response.send_message("No XP yet.")

    level = data["level"]
    xp = data["xp"]
    required = xp_for_next(level)
    percent = round((xp / required) * 100, 1)
    bar = create_bar(xp, required)

    embed = discord.Embed(
        title=f"{interaction.user.name}'s Rank",
        color=discord.Color.blue()
    )

    embed.add_field(name="Level", value=level)
    embed.add_field(name="XP", value=f"{xp}/{required} ({percent}%)", inline=False)
    embed.add_field(name="Progress", value=bar, inline=False)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="leaderboard", description="View leaderboard")
async def slash_leaderboard(interaction: discord.Interaction):
    guild_id = str(interaction.guild.id)
    top = levels.find({"guild_id": guild_id}).sort("level", -1).limit(10)

    desc = ""
    for i, user in enumerate(top, start=1):
        member = interaction.guild.get_member(int(user["user_id"]))
        name = member.name if member else "Unknown"
        desc += f"**{i}. {name}** - Level {user['level']}\n"

    embed = discord.Embed(
        title="Leaderboard",
        description=desc,
        color=discord.Color.gold()
    )

    await interaction.response.send_message(embed=embed)

# =============================
# RUN
# =============================

bot.run(TOKEN)
