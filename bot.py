import discord
from discord.ext import commands
from core.config import TOKEN, PREFIX
from core.database import db

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

bot.db = db

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

async def load():
    await bot.load_extension("cogs.leveling")
    await bot.load_extension("cogs.spawn")
    await bot.load_extension("cogs.shadows")
    await bot.load_extension("cogs.profile")
    await bot.load_extension("cogs.admin")

import asyncio
asyncio.run(load())
bot.run(TOKEN)
