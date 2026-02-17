import discord
from discord.ext import commands
from core.config import TOKEN

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

async def main():
    async with bot:
        await bot.load_extension("cogs.leveling")
        await bot.load_extension("cogs.spawn")
        await bot.load_extension("cogs.shadows")
        await bot.load_extension("cogs.profile")
        await bot.load_extension("cogs.admin")
        await bot.start(TOKEN)

import asyncio
asyncio.run(main())
