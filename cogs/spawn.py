import discord
import random
from discord.ext import commands
from database import users, guilds, shadows

SPAWN_THRESHOLD = 10


class SpawnCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_spawns = {}  # guild_id -> shadow_data


    # -------------------------
    # MESSAGE LISTENER
    # -------------------------
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        guild_id = str(message.guild.id)

        guild_data = await guilds.find_one({"guild_id": guild_id})

        if not guild_data:
            guild_data = {
                "guild_id": guild_id,
                "spawn_channel": None,
                "spawn_counter": 0
            }
            await guilds.insert_one(guild_data)

        counter = guild_data.get("spawn_counter", 0) + 1

        if counter >= SPAWN_THRESHOLD:
            await self.spawn_shadow(message)
            counter = 0

        await guilds.update_one(
            {"guild_id": guild_id},
            {"$set": {"spawn_counter": counter}}
        )


    # -------------------------
    # SPAWN SHADOW
    # -------------------------
    async def spawn_shadow(self, message: discord.Message):
        guild_id = str(message.guild.id)

        # prevent double spawn
        if self.active_spawns.get(guild_id):
            return

        shadow_list = await shadows.find({"enabled": True}).to_list(None)

        if not shadow_list:
            print("No enabled shadows in database.")
            return

        weighted_pool = []
        for s in shadow_list:
            weighted_pool.extend([s] * s.get("spawn_rate", 1))

        chosen = random.choice(weighted_pool)
        self.active_spawns[guild_id] = chosen

        # determine channel
        guild_data = await guilds.find_one({"guild_id": guild_id})
        channel_id = guild_data.get("spawn_channel")

        if channel_id:
            channel = message.guild.get_channel(int(channel_id))
        else:
            channel = message.channel  # fallback to active channel

        if not channel:
            return

        embed = discord.Embed(
            title="⚔️ A Shadow Has Appeared!",
            description="Type `!arise <name>` to capture it!",
            color=discord.Color.dark_purple()
        )

        embed.add_field(name="Rarity", value=chosen.get("rarity", "Unknown"))

        if chosen.get("image_url"):
            embed.set_image(url=chosen["image_url"])

        await channel.send(embed=embed)


    # -------------------------
    # ARISE COMMAND
    # -------------------------
    @commands.command()
    async def arise(self, ctx, *, guess: str):
        guild_id = str(ctx.guild.id)

        shadow = self.active_spawns.get(guild_id)

        if not shadow:
            return await ctx.send("❌ No active shadow.")

        if guess.lower() != shadow["name"].lower():
            return await ctx.send("❌ Wrong name.")

        user_id = str(ctx.author.id)

        user_data = await users.find_one({"user_id": user_id})

        if not user_data:
            user_data = {
                "user_id": user_id,
                "level": 1,
                "xp": 0,
                "shadows": []
            }
            await users.insert_one(user_data)

        user_data["shadows"].append({
            "name": shadow["name"],
            "level": 1,
            "xp": 0
        })

        await users.update_one(
            {"user_id": user_id},
            {"$set": {"shadows": user_data["shadows"]}}
        )

        self.active_spawns[guild_id] = None

        await ctx.send(f"🌑 {ctx.author.mention} captured **{shadow['name']}**!")


    # -------------------------
    # PROGRESS COMMAND
    # -------------------------
    @commands.command()
    async def progress(self, ctx):
        guild_data = await guilds.find_one({"guild_id": str(ctx.guild.id)})

        counter = guild_data.get("spawn_counter", 0)
        remaining = SPAWN_THRESHOLD - counter

        active = "Yes" if self.active_spawns.get(str(ctx.guild.id)) else "No"

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
            {"guild_id": str(ctx.guild.id)},
            {"$set": {"spawn_channel": channel.id}},
            upsert=True
        )

        await ctx.send(f"Spawn channel set to {channel.mention}")


async def setup(bot):
    await bot.add_cog(SpawnCog(bot))
