import discord
from discord.ext import commands
from discord import app_commands
import random
from db import users, guilds, shadows


class SpawnCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_spawns = {}  # guild_id -> shadow_data


    # --------------------------
    # MESSAGE LISTENER
    # --------------------------
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        guild_id = str(message.guild.id)
        user_id = str(message.author.id)

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

        # ---------------- SPAWN SYSTEM ----------------
        counter = guild_data.get("spawn_counter", 0) + 1

        if counter >= 40:
            await self.spawn_shadow(message.guild, message.channel)
            counter = 0

        await guilds.update_one(
            {"guild_id": guild_id},
            {"$set": {"spawn_counter": counter}}
        )


    # --------------------------
    # SPAWN SHADOW
    # --------------------------
    async def spawn_shadow(self, guild, channel):
        guild_id = str(guild.id)

        if guild_id in self.active_spawns:
            return  # already active

        shadow_list = await shadows.find({"enabled": True}).to_list(None)
        if not shadow_list:
            return

        weighted_pool = []
        for s in shadow_list:
            weighted_pool.extend([s] * s["spawn_rate"])

        chosen = random.choice(weighted_pool)

        self.active_spawns[guild_id] = chosen

        guild_data = await guilds.find_one({"guild_id": guild_id})
        spawn_channel_id = guild_data.get("spawn_channel")

        if spawn_channel_id:
            channel = guild.get_channel(spawn_channel_id)

        embed = discord.Embed(
            title="⚔️ A Shadow Has Appeared!",
            description="Type `/arise <name>` or `!arise <name>` to capture it!",
            color=discord.Color.dark_purple()
        )
        embed.set_image(url=chosen["image_url"])
        embed.add_field(name="Hint", value=f"Rarity: **{chosen['rarity']}**")

        content = guild_data.get("spawn_ping") or ""

        await channel.send(content=content, embed=embed)


    # --------------------------
    # ARISE PREFIX
    # --------------------------
    @commands.command(name="arise")
    async def arise_prefix(self, ctx, *, guess: str):
        await self.handle_arise(ctx.guild.id, ctx.author, ctx.channel, guess)


    # --------------------------
    # ARISE SLASH
    # --------------------------
    @app_commands.command(name="arise", description="Capture the spawned shadow")
    async def arise_slash(self, interaction: discord.Interaction, guess: str):
        await interaction.response.defer()
        await self.handle_arise(interaction.guild.id, interaction.user, interaction.channel, guess)
        await interaction.followup.send("Processed.")


    # --------------------------
    # HANDLE ARISE LOGIC
    # --------------------------
    async def handle_arise(self, guild_id, user, channel, guess):
        guild_id = str(guild_id)

        if guild_id not in self.active_spawns:
            return await channel.send("No active shadow.")

        shadow_data = self.active_spawns[guild_id]

        if guess.lower() != shadow_data["name"].lower():
            return await channel.send("❌ Wrong name.")

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

        del self.active_spawns[guild_id]

        embed = discord.Embed(
            title="🌑 Shadow Arisen!",
            description=f"{user.mention} captured **{shadow_data['name']}**!",
            color=discord.Color.purple()
        )

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


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setxppermsg(self, ctx, amount: int):
        await guilds.update_one(
            {"guild_id": str(ctx.guild.id)},
            {"$set": {"xp_per_msg": amount}},
            upsert=True
        )
        await ctx.send("XP per message updated.")


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setlevel(self, ctx, member: discord.Member, level: int):
        await users.update_one(
            {"user_id": str(member.id)},
            {"$set": {"level": level}},
            upsert=True
        )
        await ctx.send(f"{member.mention} level set to {level}.")


async def setup(bot):
    await bot.add_cog(SpawnCog(bot))
