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
    "cogs.advanced",
]


# =========================
# INTENTS
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

        # Load all cogs
        for cog in COGS:
            try:
                await self.load_extension(cog)
                print(f"✅ Loaded {cog}")
            except Exception as e:
                print(f"❌ Failed to load {cog}")
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

    # 🔥 GUILD SYNC (INSTANT UPDATE)
    for guild in bot.guilds:
        try:
            synced = await bot.tree.sync(guild=guild)
            print(f"🔁 Synced {len(synced)} commands to {guild.name}")
        except Exception as e:
            print(f"❌ Failed syncing {guild.name}")
            print(e)


@bot.event
async def on_guild_join(guild: discord.Guild):
    try:
        existing = await guilds.find_one({"guild_id": guild.id})

        if not existing:
            await guilds.insert_one({
                "guild_id": guild.id,
                "spawn_channel": None,
                "xp_rate": 1.0,
                "spawn_counter": 0,
                "active_spawn": None
            })

            print(f"Created config for guild: {guild.name}")

        # Sync commands instantly for new guild
        await bot.tree.sync(guild=guild)

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
