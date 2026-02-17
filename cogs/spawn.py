import discord
import random
from discord.ext import commands
from discord import app_commands
from database import users, guilds, shadows

SPAWN_THRESHOLD = 40


class SpawnCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_spawns = {}  # guild_id -> shadow_data or None


    # --------------------------
    # MESSAGE LISTENER
    # --------------------------
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        guild_id = str(message.guild.id)
        user_id = str(message.author.id)

        # ---------------- GUILD SETUP ----------------
        guild_data = await guilds.find_one({"guild_id": guild_id})
        if not guild_data:
            guild_data = {
                "guild_id": guild_id,
                "spawn_channel": None,
                "spawn_ping": None,
                "xp_per_msg": 5,
                "spawn_counter": 0
            }
            await guilds.insert_one(guild_data)

        # ---------------- XP SYSTEM ----------------
        xp_gain = guild_data.get("xp_per_msg", 5)

        user_data = await users.find_one({"user_id": user_id})
        if not user_data:
            user_data = {
                "user_id": user_id,
                "level": 1,
                "xp": 0,
                "shadows": []
            }
            await users.insert_one(user_data)

        new_xp = user_data["xp"] + xp_gain
        level = user_data["level"]
        xp_needed = level * 100
        level_up = False

        if new_xp >= xp_needed:
            level += 1
            new_xp = 0
            level_up = True

        await users.update_one(
            {"user_id": user_id},
            {"$set": {"xp": new_xp, "level": level}}
        )

        if level_up:
            embed = discord.Embed(
                title="🆙 Level Up!",
                description=f"{message.author.mention} reached **Level {level}**!",
                color=discord.Color.gold()
            )
            await message.channel.send(embed=embed)

        # ---------------- SPAWN COUNTER ----------------
        counter = guild_data.get("spawn_counter", 0) + 1

        # Only spawn if no active shadow
        if counter >= SPAWN_THRESHOLD and not self.active_spawns.get(guild_id):
            await self.spawn_shadow(message.guild)
            counter = 0

        await guilds.update_one(
            {"guild_id": guild_id},
            {"$set": {"spawn_counter": counter}}
        )


    # --------------------------
    # SPAWN SHADOW
    # --------------------------
    async def spawn_shadow(self, guild):
        guild_id = str(guild.id)

        if self.active_spawns.get(guild_id) is not None:
            return

        shadow_list = await shadows.find({"enabled": True}).to_list(None)
        if not shadow_list:
            return

        weighted_pool = []
        for s in shadow_list:
            weighted_pool.extend([s] * s.get("spawn_rate", 1))

        chosen = random.choice(weighted_pool)
        self.active_spawns[guild_id] = chosen

        guild_data = await guilds.find_one({"guild_id": guild_id})

        # SAFE CHANNEL FETCH
        channel = None
        channel_id = guild_data.get("spawn_channel")

        if channel_id:
            try:
                channel = guild.get_channel(int(channel_id))
            except:
                channel = None

        if not channel:
            channel = guild.system_channel

        if not channel:
            print(f"❌ No valid spawn channel in guild {guild.name}")
            return

        embed = discord.Embed(
            title="⚔️ A Shadow Has Appeared!",
            description="Type `/arise <name>` or `!arise <name>` to capture it!",
            color=discord.Color.dark_purple()
        )

        embed.set_image(url=chosen.get("image_url"))
        embed.add_field(name="Name", value=chosen.get("name"), inline=True)
        embed.add_field(name="Rarity", value=chosen.get("rarity", "Unknown"), inline=True)

        content = guild_data.get("spawn_ping") or ""

        await channel.send(content=content, embed=embed)


    # --------------------------
    # ARISE PREFIX
    # --------------------------
    @commands.command(name="arise")
    async def arise_prefix(self, ctx, *, guess: str):
        result = await self.handle_arise(ctx.guild, ctx.author, ctx.channel, guess)
        await ctx.send(result)


    # --------------------------
    # ARISE SLASH
    # --------------------------
    @app_commands.command(name="arise", description="Capture the spawned shadow")
    async def arise_slash(self, interaction: discord.Interaction, guess: str):
        if not interaction.guild:
            return await interaction.response.send_message("Guild only.", ephemeral=True)

        result = await self.handle_arise(
            interaction.guild,
            interaction.user,
            interaction.channel,
            guess
        )

        await interaction.response.send_message(result)


    # --------------------------
    # HANDLE ARISE
    # --------------------------
    async def handle_arise(self, guild, user, channel, guess):
        guild_id = str(guild.id)

        shadow_data = self.active_spawns.get(guild_id)

        if not shadow_data:
            return "❌ No active shadow."

        if guess.lower() != shadow_data["name"].lower():
            return "❌ Wrong name."

        user_id = str(user.id)
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
            "name": shadow_data["name"],
            "level": 1,
            "xp": 0
        })

        await users.update_one(
            {"user_id": user_id},
            {"$set": {"shadows": user_data["shadows"]}}
        )

        self.active_spawns[guild_id] = None

        embed = discord.Embed(
            title="🌑 Shadow Arisen!",
            description=f"{user.mention} captured **{shadow_data['name']}**!",
            color=discord.Color.purple()
        )

        await channel.send(embed=embed)

        return "Shadow captured!"


    # --------------------------
    # PROGRESS COMMAND
    # --------------------------
    @commands.command(name="progress")
    async def progress_prefix(self, ctx):
        await self.show_progress(ctx.guild, ctx.channel)


    @app_commands.command(name="progress", description="See spawn progress")
    async def progress_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.show_progress(interaction.guild, interaction.channel)
        await interaction.followup.send("Progress shown.")


    async def show_progress(self, guild, channel):
        guild_data = await guilds.find_one({"guild_id": str(guild.id)})
        counter = guild_data.get("spawn_counter", 0)
        remaining = max(0, SPAWN_THRESHOLD - counter)

        percent = int((counter / SPAWN_THRESHOLD) * 100)
        filled = int(counter / 4)
        bar = "█" * filled + "░" * (10 - filled)

        active = "Yes" if self.active_spawns.get(str(guild.id)) else "No"

        embed = discord.Embed(
            title="📊 Shadow Spawn Progress",
            color=discord.Color.blurple()
        )

        embed.add_field(name="Progress", value=f"`{bar}` {percent}%", inline=False)
        embed.add_field(name="Messages", value=f"{counter}/{SPAWN_THRESHOLD}", inline=True)
        embed.add_field(name="Remaining", value=str(remaining), inline=True)
        embed.add_field(name="Active Spawn", value=active, inline=False)

        await channel.send(embed=embed)


    # --------------------------
    # ADMIN COMMANDS
    # --------------------------
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setspawnchannel(self, ctx, channel: discord.TextChannel):
        await guilds.update_one(
            {"guild_id": str(ctx.guild.id)},
            {"$set": {"spawn_channel": channel.id}},
            upsert=True
        )
        await ctx.send("Spawn channel set.")


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setspawnping(self, ctx, ping: str):
        await guilds.update_one(
            {"guild_id": str(ctx.guild.id)},
            {"$set": {"spawn_ping": ping}},
            upsert=True
        )
        await ctx.send("Spawn ping set.")


async def setup(bot):
    await bot.add_cog(SpawnCog(bot))
