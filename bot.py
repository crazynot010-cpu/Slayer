import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from config import PREFIX

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

async def main():
    async with bot:
        await bot.load_extension("cogs.events")
        await bot.load_extension("cogs.spawn")
        await bot.start(os.getenv("TOKEN"))

import asyncio
asyncio.run(main())
