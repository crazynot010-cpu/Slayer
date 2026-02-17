import discord
from discord.ext import commands, tasks
from discord import app_commands
from pymongo import MongoClient
import os
import random
import time
import math

# ================= CONFIG =================

TOKEN = os.getenv("TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

SPAWN_MIN_MESSAGES = 30
SPAWN_MAX_MESSAGES = 60
SPAWN_TRIGGER_CHANCE = 0.43
SPAWN_TIMEOUT = 300

ARISE_SUCCESS = 0.55
MAX_DUPES = 3
MAX_SLOTS = 16

# ==========================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

client = MongoClient(MONGO_URI)
db = client["solo_leveling"]
users = db["users"]
guilds = db["guilds"]
shadows = db["shadows"]

# ================= UTIL =================

def xp_required(level):
    return int(100 * level + (level ** 2 * 25))

def xp_bar(current, required, length=20):
    percent = current / required
    filled = int(length * percent)
    return "█" * filled + "░" * (length - filled)

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

# ================= AUTO CLEANUP =================

@tasks.loop(seconds=30)
async def cleanup_spawns():
    for guild_data in guilds.find({"active_spawn": {"$ne": None}}):
        spawn = guild_data["active_spawn"]
        if spawn and time.time() > spawn["expires"]:
            guilds.update_one(
                {"guild_id": guild_data["guild_id"]},
                {"$set": {"active_spawn": None}}
            )

# ================= XP + SPAWN =================

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    guild_data = get_guild(message.guild.id)
    user_data = get_user(message.author.id)

    # XP Gain
    xp_gain = random.randint(5, 15)
    users.update_one({"user_id": message.author.id}, {"$inc": {"xp": xp_gain}})

    user_data = get_user(message.author.id)

    # Level Up
    while user_data["xp"] >= xp_required(user_data["level"]):
        users.update_one(
            {"user_id": message.author.id},
            {"$inc": {"level": 1}, "$set": {"xp": 0}}
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

    # Spawn counter
    guilds.update_one(
        {"guild_id": message.guild.id},
        {"$inc": {"message_count": 1}}
    )

    guild_data = get_guild(message.guild.id)

    if guild_data["message_count"] >= guild_data["next_spawn"]:
        guilds.update_one(
            {"guild_id": message.guild.id},
            {"$set": {
                "message_count": 0,
                "next_spawn": random.randint(SPAWN_MIN_MESSAGES, SPAWN_MAX_MESSAGES)
            }}
        )

        if random.random() <= SPAWN_TRIGGER_CHANCE:
            await spawn_shadow(message.guild)

    await bot.process_commands(message)

# ================= SPAWN =================

async def spawn_shadow(guild):
    guild_data = get_guild(guild.id)

    if guild_data["active_spawn"]:
        return

    if not guild_data["spawn_channel"]:
        return

    channel = guild.get_channel(guild_data["spawn_channel"])
    if not channel:
        return

    shadow_list = list(shadows.find())
    if not shadow_list:
        return

    # Weighted spawn
    weights = [s.get("spawnchance", 1) for s in shadow_list]
    chosen = random.choices(shadow_list, weights=weights, k=1)[0]

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
        description="Use `!arise <name>`",
        color=discord.Color.dark_purple()
    )
    embed.set_image(url=chosen["image"])

    content = ""
    if guild_data["ping_role"]:
        content = f"<@&{guild_data['ping_role']}>"

    await channel.send(content=content, embed=embed)

# ================= ARISE =================

async def arise_logic(ctx, name):
    guild_data = get_guild(ctx.guild.id)
    spawn = guild_data.get("active_spawn")

    if not spawn:
        return await ctx.send("No shadow has spawned!")

    if spawn["claimed"]:
        return await ctx.send("Already claimed!")

    if time.time() > spawn["expires"]:
        guilds.update_one(
            {"guild_id": ctx.guild.id},
            {"$set": {"active_spawn": None}}
        )
        return await ctx.send("Shadow vanished!")

    if name.lower() != spawn["name"].lower():
        return await ctx.send("Wrong name!")

    if random.random() > ARISE_SUCCESS:
        users.update_one({"user_id": ctx.author.id}, {"$inc": {"xp": 10}})
        return await ctx.send("Arise failed!")

    user = get_user(ctx.author.id)

    if len(user["shadows"]) >= MAX_SLOTS:
        return await ctx.send("Slots full!")

    count = sum(1 for s in user["shadows"] if s["name"] == spawn["name"])
    if count >= MAX_DUPES:
        return await ctx.send("Max duplicates reached!")

    users.update_one(
        {"user_id": ctx.author.id},
        {
            "$push": {"shadows": spawn},
            "$inc": {"xp": 75}
        }
    )

    guilds.update_one(
        {"guild_id": ctx.guild.id},
        {"$set": {"active_spawn": None}}
    )

    await ctx.send(f"{ctx.author.mention} has arisen **{spawn['name']}**!")

@bot.command()
async def arise(ctx, name: str):
    await arise_logic(ctx, name)

@bot.tree.command(name="arise")
async def arise_slash(interaction: discord.Interaction, name: str):
    await interaction.response.defer()
    await arise_logic(interaction.channel, name)

# ================= SHADOW ADMIN =================

@bot.command()
@commands.has_permissions(administrator=True)
async def addshadow(ctx, name, rarity, spawnchance: float, image, defense: int, damage: int, stamina: int):
    shadows.insert_one({
        "name": name,
        "rarity": rarity,
        "spawnchance": spawnchance,
        "image": image,
        "defense": defense,
        "damage": damage,
        "stamina": stamina
    })
    await ctx.send("Shadow added globally.")

@bot.command()
@commands.has_permissions(administrator=True)
async def statsshdw(ctx, name, defense: int, damage: int, stamina: int):
    shadows.update_one(
        {"name": name},
        {"$set": {"defense": defense, "damage": damage, "stamina": stamina}}
    )
    await ctx.send("Stats updated.")

@bot.command()
async def viewshadow(ctx, name):
    shadow = shadows.find_one({"name": name})
    if not shadow:
        return await ctx.send("Not found.")

    embed = discord.Embed(
        title=shadow["name"],
        description=f"Rarity: {shadow['rarity']}\nDEF: {shadow['defense']}\nDMG: {shadow['damage']}\nSTM: {shadow['stamina']}",
        color=discord.Color.dark_purple()
    )
    embed.set_image(url=shadow["image"])
    await ctx.send(embed=embed)

# ================= PROFILE =================

@bot.command()
async def profile(ctx, member: discord.Member = None):
    member = member or ctx.author
    user = get_user(member.id)

    required = xp_required(user["level"])
    bar = xp_bar(user["xp"], required)

    await ctx.send(
        f"**{member.name}**\n"
        f"Level: {user['level']}\n"
        f"XP: {user['xp']} / {required}\n"
        f"{bar}\n"
        f"Shadows: {len(user['shadows'])}/{MAX_SLOTS}"
    )

# ================= SETTINGS =================

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

# ================= HELP =================

@bot.command()
async def help(ctx):
    await ctx.send("""
**Solo Leveling Bot**

!profile  
!arise <name>  
!viewshadow <name>  

Admin:
!addshadow  
!statsshdw  
!setchannelspawn  
!setpingrole  
""")

# ================= READY =================

@bot.event
async def on_ready():
    cleanup_spawns.start()
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

bot.run(TOKEN)
