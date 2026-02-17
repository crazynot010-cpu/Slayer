import discord
from discord.ext import commands, tasks
from pymongo import MongoClient
import os
import random
import time
import math

# ================== CONFIG ==================

TOKEN = os.getenv("TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

SPAWN_MIN_MESSAGES = 30
SPAWN_MAX_MESSAGES = 60
SPAWN_CHANCE = 0.43
SPAWN_TIMEOUT = 300

ARISE_SUCCESS_RATE = 0.55

MAX_DUPES = 3
MAX_SLOTS = 16

# ============================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

client = MongoClient(MONGO_URI)
db = client["solo_leveling"]
users = db["users"]
guilds = db["guilds"]
shadows = db["shadows"]

# ================== UTIL ==================

def xp_required(level):
    return int(100 * level + (level ** 2 * 25))

def get_user(user_id):
    user = users.find_one({"user_id": user_id})
    if not user:
        user = {
            "user_id": user_id,
            "xp": 0,
            "level": 1,
            "shadows": []
        }
        users.insert_one(user)
    return user

def get_guild(guild_id):
    data = guilds.find_one({"guild_id": guild_id})
    if not data:
        data = {
            "guild_id": guild_id,
            "message_count": 0,
            "spawn_channel": None,
            "ping_role": None,
            "active_spawn": None,
            "next_spawn": random.randint(SPAWN_MIN_MESSAGES, SPAWN_MAX_MESSAGES)
        }
        guilds.insert_one(data)
    return data

# ================== XP SYSTEM ==================

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    guild_data = get_guild(message.guild.id)
    user_data = get_user(message.author.id)

    # XP gain
    xp_gain = random.randint(5, 15)
    users.update_one(
        {"user_id": message.author.id},
        {"$inc": {"xp": xp_gain}}
    )

    user_data = get_user(message.author.id)

    # Level up check
    while user_data["xp"] >= xp_required(user_data["level"]):
        users.update_one(
            {"user_id": message.author.id},
            {
                "$inc": {"level": 1},
                "$set": {"xp": 0}
            }
        )
        user_data = get_user(message.author.id)

        await message.channel.send(
            f"{message.author.mention} leveled up to **Level {user_data['level']}!**"
        )

        role_name = f"Level {user_data['level']}"
        role = discord.utils.get(message.guild.roles, name=role_name)

        if not role:
            role = await message.guild.create_role(name=role_name)

        await message.author.add_roles(role)

    # Spawn system
    guilds.update_one(
        {"guild_id": message.guild.id},
        {"$inc": {"message_count": 1}}
    )

    guild_data = get_guild(message.guild.id)

    if guild_data["message_count"] >= guild_data["next_spawn"]:
        guilds.update_one(
            {"guild_id": message.guild.id},
            {"$set": {"message_count": 0,
                      "next_spawn": random.randint(SPAWN_MIN_MESSAGES, SPAWN_MAX_MESSAGES)}}
        )

        if random.random() <= SPAWN_CHANCE:
            await spawn_shadow(message.guild, message.channel)

    await bot.process_commands(message)

# ================== SPAWN ==================

async def spawn_shadow(guild, channel):
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

    embed = discord.Embed(
        title="A Shadow Has Appeared!",
        description="Use `!arise <name>` to capture it!",
        color=discord.Color.dark_purple()
    )
    embed.set_image(url=chosen["image"])

    await channel.send(embed=embed)

# ================== ARISE ==================

@bot.command()
async def arise(ctx, name: str):
    guild_data = get_guild(ctx.guild.id)

    spawn = guild_data.get("active_spawn")
    if not spawn:
        return await ctx.send("No shadow has spawned!")

    if spawn["claimed"]:
        return await ctx.send("This shadow was already claimed!")

    if time.time() > spawn["expires"]:
        guilds.update_one(
            {"guild_id": ctx.guild.id},
            {"$set": {"active_spawn": None}}
        )
        return await ctx.send("The shadow vanished...")

    if name.lower() != spawn["name"].lower():
        return await ctx.send("Wrong shadow name!")

    if random.random() > ARISE_SUCCESS_RATE:
        users.update_one({"user_id": ctx.author.id}, {"$inc": {"xp": 10}})
        return await ctx.send("Arise failed! Try again!")

    user = get_user(ctx.author.id)

    if len(user["shadows"]) >= MAX_SLOTS:
        return await ctx.send("Your shadow slots are full!")

    count = sum(1 for s in user["shadows"] if s["name"] == spawn["name"])
    if count >= MAX_DUPES:
        return await ctx.send("Max duplicate reached!")

    users.update_one(
        {"user_id": ctx.author.id},
        {"$push": {"shadows": {"name": spawn["name"], "rarity": spawn.get("rarity", "Unknown")}},
         "$inc": {"xp": 75}}
    )

    guilds.update_one(
        {"guild_id": ctx.guild.id},
        {"$set": {"active_spawn": None}}
    )

    await ctx.send(f"{ctx.author.mention} has successfully arisen **{spawn['name']}**!")

# ================== SHADOW ADMIN ==================

@bot.command()
@commands.has_permissions(administrator=True)
async def addshadow(ctx, name, rarity, spawnchance: float, image):
    shadows.insert_one({
        "name": name,
        "rarity": rarity,
        "spawnchance": spawnchance,
        "image": image
    })
    await ctx.send("Shadow added globally.")

@bot.command()
@commands.has_permissions(administrator=True)
async def removeshadow(ctx, name):
    shadows.delete_one({"name": name})
    await ctx.send("Shadow removed.")

@bot.command()
async def viewshadow(ctx, name):
    shadow = shadows.find_one({"name": name})
    if not shadow:
        return await ctx.send("Shadow not found.")

    embed = discord.Embed(
        title=shadow["name"],
        description=f"Rarity: {shadow['rarity']}",
        color=discord.Color.dark_purple()
    )
    embed.set_image(url=shadow["image"])
    await ctx.send(embed=embed)

# ================== SETTINGS ==================

@bot.command()
@commands.has_permissions(administrator=True)
async def setchannelspawn(ctx, channel: discord.TextChannel):
    guilds.update_one({"guild_id": ctx.guild.id}, {"$set": {"spawn_channel": channel.id}}, upsert=True)
    await ctx.send("Spawn channel set.")

@bot.command()
@commands.has_permissions(administrator=True)
async def setpingrole(ctx, role: discord.Role):
    guilds.update_one({"guild_id": ctx.guild.id}, {"$set": {"ping_role": role.id}}, upsert=True)
    await ctx.send("Ping role set.")

# ================== PROFILE ==================

@bot.command()
async def profile(ctx, member: discord.Member = None):
    member = member or ctx.author
    user = get_user(member.id)

    await ctx.send(
        f"**{member.name}**\n"
        f"Level: {user['level']}\n"
        f"XP: {user['xp']} / {xp_required(user['level'])}\n"
        f"Shadows: {len(user['shadows'])}/{MAX_SLOTS}"
    )

# ================== HELP ==================

@bot.command()
async def help(ctx):
    await ctx.send("""
**Solo Leveling Bot Commands**

!profile  
!arise <name>  
!viewshadow <name>  

Admin:
!addshadow  
!removeshadow  
!setchannelspawn  
!setpingrole  
""")

# ==================

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

bot.run(TOKEN)
