import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio

SPAWN_THRESHOLD = 10  # Messages required

class Spawn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guilds = bot.db.guilds
        self.users = bot.db.users

    # ===============================
    # MESSAGE LISTENER (SPAWN LOGIC)
    # ===============================
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        guild_id = message.guild.id

        guild_data = await self.guilds.find_one({"guild_id": guild_id})

        if not guild_data:
            guild_data = {
                "guild_id": guild_id,
                "spawn_counter": 0,
                "active_spawn": None
            }
            await self.guilds.insert_one(guild_data)

        # If spawn active → don't count
        if guild_data.get("active_spawn"):
            await self.bot.process_commands(message)
            return

        counter = guild_data.get("spawn_counter", 0) + 1

        if counter >= SPAWN_THRESHOLD:
            counter = 0
            await self.guilds.update_one(
                {"guild_id": guild_id},
                {"$set": {"spawn_counter": counter}}
            )
            await self.spawn_shadow(message.guild, message.channel)
        else:
            await self.guilds.update_one(
                {"guild_id": guild_id},
                {"$set": {"spawn_counter": counter}}
            )

        await self.bot.process_commands(message)

    # ===============================
    # SPAWN SHADOW
    # ===============================
    async def spawn_shadow(self, guild, channel):
        guild_id = guild.id

        shadows = [
            {"name": "Igris", "xp": 50},
            {"name": "Tank", "xp": 35},
            {"name": "Iron", "xp": 25}
        ]

        shadow = random.choice(shadows)

        await self.guilds.update_one(
            {"guild_id": guild_id},
            {
                "$set": {
                    "active_spawn": {
                        "name": shadow["name"],
                        "xp": shadow["xp"]
                    }
                }
            }
        )

        embed = discord.Embed(
            title="A Shadow Has Appeared!",
            description=f"Type `/arise {shadow['name']}` to claim it!",
            color=discord.Color.dark_purple()
        )

        await channel.send(embed=embed)

        # Auto despawn after 2 minutes
        await asyncio.sleep(120)

        guild_data = await self.guilds.find_one({"guild_id": guild_id})
        if guild_data and guild_data.get("active_spawn"):
            await self.guilds.update_one(
                {"guild_id": guild_id},
                {"$set": {"active_spawn": None}}
            )
            await channel.send("The shadow vanished...")

    # ===============================
    # ARISE (PREFIX)
    # ===============================
    @commands.command()
    async def arise(self, ctx, shadow_name: str):
        msg, success = await self.attempt_arise(ctx.guild.id, ctx.author, shadow_name)

        if success:
            await ctx.send(f"✅ {msg}")
        else:
            await ctx.send(f"❌ {msg}")

    # ===============================
    # ARISE (SLASH)
    # ===============================
    @app_commands.command(name="arise", description="Claim a spawned shadow")
    async def arise_slash(self, interaction: discord.Interaction, shadow_name: str):
        msg, success = await self.attempt_arise(
            interaction.guild.id,
            interaction.user,
            shadow_name
        )

        if success:
            await interaction.response.send_message(f"✅ {msg}")
        else:
            await interaction.response.send_message(f"❌ {msg}", ephemeral=True)

    # ===============================
    # ARISE LOGIC
    # ===============================
    async def attempt_arise(self, guild_id, user, shadow_name):
        guild_data = await self.guilds.find_one({"guild_id": guild_id})

        if not guild_data or not guild_data.get("active_spawn"):
            return "No shadow has spawned!", False

        active = guild_data["active_spawn"]

        if active["name"].lower() != shadow_name.lower():
            return "Wrong shadow name!", False

        # Clear spawn immediately (prevents stuck bug)
        await self.guilds.update_one(
            {"guild_id": guild_id},
            {"$set": {"active_spawn": None}}
        )

        # Give XP
        await self.users.update_one(
            {"user_id": user.id},
            {"$inc": {"xp": active["xp"]}},
            upsert=True
        )

        return f"You caught {active['name']} and gained {active['xp']} XP!", True

    # ===============================
    # PROGRESS
    # ===============================
    @commands.command()
    async def progress(self, ctx):
        guild_data = await self.guilds.find_one({"guild_id": ctx.guild.id})

        counter = guild_data.get("spawn_counter", 0)
        active = "Yes" if guild_data.get("active_spawn") else "No"

        embed = discord.Embed(
            title="Spawn Progress",
            color=discord.Color.blue()
        )
        embed.add_field(name="Messages", value=f"{counter}/{SPAWN_THRESHOLD}")
        embed.add_field(name="Remaining", value=str(SPAWN_THRESHOLD - counter))
        embed.add_field(name="Active Spawn", value=active)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Spawn(bot))
