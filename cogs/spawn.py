import discord
import random
from discord.ext import commands
from database import guilds, shadows

SPAWN_THRESHOLD = 10


class SpawnCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # -------------------------
    # MESSAGE LISTENER
    # -------------------------
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        guild_id = message.guild.id

        guild_data = await guilds.find_one({"guild_id": guild_id})

        if not guild_data:
            guild_data = {
                "guild_id": guild_id,
                "spawn_channel": None,
                "spawn_counter": 0,
                "active_spawn": None
            }
            await guilds.insert_one(guild_data)

        # If a shadow is already active → don't count messages
        if guild_data.get("active_spawn"):
            return

        counter = guild_data.get("spawn_counter", 0) + 1

        if counter >= SPAWN_THRESHOLD:
            await self.spawn_shadow(message.guild, message.channel)
            counter = 0

        await guilds.update_one(
            {"guild_id": guild_id},
            {"$set": {"spawn_counter": counter}}
        )

    # -------------------------
    # SPAWN SHADOW
    # -------------------------
    async def spawn_shadow(self, guild: discord.Guild, fallback_channel: discord.TextChannel):
        guild_id = guild.id

        shadow_list = await shadows.find({"enabled": True}).to_list(None)

        if not shadow_list:
            print("No enabled shadows in database.")
            return

        weighted_pool = []
        for s in shadow_list:
            weighted_pool.extend([s] * s.get("spawn_rate", 1))

        chosen = random.choice(weighted_pool)

        # Save to MongoDB
        await guilds.update_one(
            {"guild_id": guild_id},
            {
                "$set": {
                    "active_spawn": {
                        "name": chosen["name"],
                        "rarity": chosen["rarity"],
                        "base_power": chosen.get("base_power", 0),
                        "claimed_by": None
                    }
                }
            }
        )

        guild_data = await guilds.find_one({"guild_id": guild_id})
        channel_id = guild_data.get("spawn_channel")

        if channel_id:
            channel = guild.get_channel(int(channel_id))
        else:
            channel = fallback_channel

        if not channel:
            return

        embed = discord.Embed(
            title="⚔️ A Shadow Has Appeared!",
            description=f"Type `!arise` to capture **{chosen['name']}**!",
            color=discord.Color.dark_purple()
        )

        embed.add_field(
            name="Rarity",
            value=chosen.get("rarity", "Unknown")
        )

        if chosen.get("image_url"):
            embed.set_image(url=chosen["image_url"])

        await channel.send(embed=embed)

    # -------------------------
    # PROGRESS COMMAND
    # -------------------------
    @commands.command()
    async def progress(self, ctx):
        guild_data = await guilds.find_one({"guild_id": ctx.guild.id})

        if not guild_data:
            return await ctx.send("No data for this server yet.")

        counter = guild_data.get("spawn_counter", 0)
        remaining = max(0, SPAWN_THRESHOLD - counter)

        active = "Yes" if guild_data.get("active_spawn") else "No"

        embed = discord.Embed(
            title="📊 Spawn Progress",
            color=discord.Color.blurple()
        )

        embed.add_field(name="Messages", value=f"{counter}/{SPAWN_THRESHOLD}")
        embed.add_field(name="Remaining", value=str(remaining))
        embed.add_field(name="Active Spawn", value=active)

        await ctx.send(embed=embed)

    # -------------------------
    # SET SPAWN CHANNEL
    # -------------------------
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setspawnchannel(self, ctx, channel: discord.TextChannel):
        await guilds.update_one(
            {"guild_id": ctx.guild.id},
            {"$set": {"spawn_channel": channel.id}},
            upsert=True
        )

        await ctx.send(f"Spawn channel set to {channel.mention}")


async def setup(bot):
    await bot.add_cog(SpawnCog(bot))
