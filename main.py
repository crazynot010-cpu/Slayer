import discord
from discord.ext import commands
import asyncio

from config import TOKEN
from database import guilds


# =========================
# COGS
# =========================

COGS = [
    "cogs.xp",
    "cogs.ranks",
    "cogs.spawn",
    "cogs.arise",
    "cogs.inventory",
    "cogs.shadows",
    "cogs.profile",
    "cogs.leaderboard",
    "cogs.admin",
    "cogs.stats",
    "cogs.help",
]


# =========================
# INTENTS (CLEAN & SAFE)
# =========================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True


# =========================
# BOT CLASS
# =========================

class ShadowBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):

        print("Loading cogs...")

        for cog in COGS:
            try:
                await self.load_extension(cog)
                print(f"✅ Loaded {cog}")
            except Exception as e:
                print(f"❌ Failed to load {cog}")
                print(e)

        try:
            synced = await self.tree.sync()
            print(f"🔁 Synced {len(synced)} slash commands.")
        except Exception as e:
            print("❌ Slash sync failed:")
            print(e)


bot = ShadowBot()


# =========================
# EVENTS
# =========================

@bot.event
async def on_ready():
    print("-----------------------------------")
    print(f"Logged in as {bot.user}")
    print(f"Bot ID: {bot.user.id}")
    print("-----------------------------------")


@bot.event
async def on_guild_join(guild: discord.Guild):
    try:
        existing = await guilds.find_one({"guild_id": guild.id})

        if not existing:
            await guilds.insert_one({
                "guild_id": guild.id,
                "spawn_channel": None,
                "xp_rate": 1.0,
                "message_count": 0,
                "next_spawn_threshold": 45,
                "active_spawn": None
            })

            print(f"Created config for guild: {guild.name}")

    except Exception as e:
        print(f"Error creating guild config for {guild.name}:")
        print(e)


# =========================
# GLOBAL ERROR HANDLER
# =========================

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return

    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
        return

    await ctx.send(f"⚠️ Error: {str(error)}")


# =========================
# START
# =========================

if __name__ == "__main__":
    asyncio.run(bot.start(TOKEN))
