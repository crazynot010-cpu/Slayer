import discord
from discord.ext import commands
from config import TOKEN
from database import guilds

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

intents = discord.Intents.all()

class ShadowBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        for cog in COGS:
            try:
                await self.load_extension(cog)
                print(f"Loaded {cog}")
            except Exception as e:
                print(f"Failed to load {cog}: {e}")

        await self.tree.sync()

bot = ShadowBot()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")

@bot.event
async def on_guild_join(guild: discord.Guild):
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

if __name__ == "__main__":
    bot.run(TOKEN)
