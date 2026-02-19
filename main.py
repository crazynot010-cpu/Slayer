import discord
from discord.ext import commands, tasks
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Database
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client["mmorpg"]

bot.db = db

# =========================
# READY EVENT
# =========================

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")
    spawn_loop.start()

# =========================
# XP FROM MESSAGES
# =========================

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user = await db.users.find_one({"_id": message.author.id})

    if not user:
        await db.users.insert_one({
            "_id": message.author.id,
            "xp": 0,
            "level": 1,
            "hp": 100,
            "ce": 50,
            "dmg": 10,
            "stat_points": 0,
            "money": 0,
            "inventory": [],
            "equipped": {},
            "mastery": {}
        })
    else:
        xp_gain = 5
        new_xp = user["xp"] + xp_gain

        level = user["level"]
        xp_needed = level * 100

        if new_xp >= xp_needed:
            level += 1
            await db.users.update_one(
                {"_id": message.author.id},
                {"$set": {
                    "xp": 0,
                    "level": level
                },
                 "$inc": {
                     "stat_points": 5,
                     "hp": 15,
                     "ce": 10,
                     "dmg": 5
                 }}
            )
        else:
            await db.users.update_one(
                {"_id": message.author.id},
                {"$set": {"xp": new_xp}}
            )

    await bot.process_commands(message)

# =========================
# SPAWN LOOP (NPC)
# =========================

@tasks.loop(minutes=1)
async def spawn_loop():
    npcs = bot.db.npcs.find({"auto_spawn": True})

    async for npc in npcs:
        channels = npc.get("spawn_channels", [])

        for channel_id in channels:
            channel = bot.get_channel(channel_id)
            if channel:
                embed = discord.Embed(
                    title=f"{npc['name']} has appeared!",
                    description="Defeat it before it disappears!",
                    color=discord.Color.red()
                )

                if npc.get("image_url"):
                    embed.set_image(url=npc["image_url"])

                await channel.send(embed=embed)

# =========================
# LOAD COGS
# =========================

async def load_extensions():
    await bot.load_extension("cogs.admin")
    await bot.load_extension("cogs.player")
    await bot.load_extension("cogs.combat")
    await bot.load_extension("cogs.raid")
    await bot.load_extension("cogs.market")

bot.loop.create_task(load_extensions())

bot.run(TOKEN)
