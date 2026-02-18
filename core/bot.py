import discord
from discord.ext import commands
from discord import app_commands

from models.shadow_model import ShadowModel
from models.user_model import UserModel
from models.guild_model import GuildModel
from systems.spawn_system import SpawnSystem
from systems.arise_system import AriseSystem
from systems.xp_system import XPSystem

import asyncio
import time


XP_PER_MESSAGE = 25

# 🔥 PUT YOUR SERVER ID HERE
GUILD_ID = 123456789012345678


class SoloLevelingBot(commands.Bot):

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix=None,
            intents=intents
        )

    # ==========================================
    # FIXED SLASH SYNC (INSTANT)
    # ==========================================
    async def setup_hook(self):

        guild = discord.Object(id=GUILD_ID)

        # Clear previous guild commands
        self.tree.clear_commands(guild=guild)

        # Sync instantly to your server
        await self.tree.sync(guild=guild)

        print("Instant guild slash sync complete.")

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")

    # ==========================================
    # MESSAGE EVENT (XP + SPAWN)
    # ==========================================
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        guild_id = message.guild.id
        user_id = message.author.id

        # XP
        await XPSystem.add_xp(user_id, guild_id, XP_PER_MESSAGE, message.author)

        # Spawn counter
        await SpawnSystem.increment_message(guild_id)

        spawn = await SpawnSystem.try_spawn(guild_id)

        if spawn:
            guild_data = await GuildModel.get(guild_id)

            channel_id = guild_data.get("spawn_channel_id")
            ping_role_id = guild_data.get("ping_role_id")

            channel = message.guild.get_channel(channel_id) if channel_id else message.channel

            ping_text = ""
            if ping_role_id:
                role = message.guild.get_role(ping_role_id)
                if role:
                    ping_text = role.mention

            embed = discord.Embed(
                title="A Shadow Has Appeared...",
                description="Use `/arise <name>` to claim it.",
                color=discord.Color.dark_purple()
            )
            embed.set_image(url=spawn["image"])

            sent_msg = await channel.send(content=ping_text, embed=embed)

            expire_time = int(time.time()) + 120

            await GuildModel.update(
                guild_id,
                {
                    "spawn_message_id": sent_msg.id,
                    "spawn_expires_at": expire_time
                }
            )

            async def expire():
                await asyncio.sleep(120)

                guild_data = await GuildModel.get(guild_id)
                if guild_data.get("active_spawn"):
                    await SpawnSystem.clear_spawn(guild_id)
                    try:
                        await sent_msg.delete()
                    except:
                        pass

            self.loop.create_task(expire())

    # ==========================================
    # ADMIN SHADOW COMMANDS
    # ==========================================

    @app_commands.command(name="addshadow", description="Add a new shadow (Admin only)")
    async def addshadow(self, interaction: discord.Interaction,
                        name: str,
                        rarity: str,
                        spawnchance: float,
                        imageurl: str):

        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Admin only.", ephemeral=True)

        await ShadowModel.create(name, rarity, spawnchance, imageurl)
        await interaction.response.send_message(f"Shadow `{name}` created.")

    @app_commands.command(name="removeshadow", description="Remove a shadow (Admin only)")
    async def removeshadow(self, interaction: discord.Interaction, name: str):

        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Admin only.", ephemeral=True)

        await ShadowModel.delete(name)
        await interaction.response.send_message(f"Shadow `{name}` removed.")

    @app_commands.command(name="statsshdw", description="Update shadow stats")
    async def statsshdw(self, interaction: discord.Interaction,
                        name: str,
                        dmg: int,
                        defense: int,
                        stamina: int):

        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Admin only.", ephemeral=True)

        await ShadowModel.update_stats(name, defense, dmg, stamina)
        await interaction.response.send_message(f"Stats updated for `{name}`.")

    # ==========================================
    # SPAWN SETTINGS
    # ==========================================

    @app_commands.command(name="setspawnchannel", description="Set spawn channel")
    async def setspawnchannel(self, interaction: discord.Interaction, channel: discord.TextChannel):

        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Admin only.", ephemeral=True)

        await GuildModel.update(interaction.guild.id, {"spawn_channel_id": channel.id})
        await interaction.response.send_message(f"Spawn channel set to {channel.mention}")

    @app_commands.command(name="setspawnping", description="Set spawn ping role")
    async def setspawnping(self, interaction: discord.Interaction, role: discord.Role):

        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Admin only.", ephemeral=True)

        await GuildModel.update(interaction.guild.id, {"ping_role_id": role.id})
        await interaction.response.send_message(f"Spawn ping role set to {role.mention}")

    # ==========================================
    # ARISE
    # ==========================================

    @app_commands.command(name="arise", description="Claim active shadow")
    async def arise(self, interaction: discord.Interaction, name: str):

        result = await AriseSystem.attempt(
            interaction.user.id,
            interaction.guild.id,
            name
        )

        if not result["success"]:
            reason = result["reason"]

            if reason == "no_spawn":
                return await interaction.response.send_message("No active shadow.", ephemeral=True)

            if reason == "wrong_name":
                return await interaction.response.send_message("Wrong name.", ephemeral=True)

            if reason == "max_dupe":
                return await interaction.response.send_message(
                    "You already own 3 copies of this shadow.",
                    ephemeral=True
                )

        await interaction.response.send_message(
            f"{interaction.user.mention} has arisen **{result['shadow']}**!"
        )

    # ==========================================
    # PROFILE
    # ==========================================

    @app_commands.command(name="profile", description="View your profile")
    async def profile(self, interaction: discord.Interaction):

        user = await UserModel.get(interaction.user.id, interaction.guild.id)

        embed = discord.Embed(
            title=f"{interaction.user.display_name}'s Profile",
            color=discord.Color.dark_purple()
        )

        embed.add_field(name="Level", value=user["level"])
        embed.add_field(name="XP", value=user["xp"])
        embed.add_field(name="Shadows", value=len(user["shadows"]))

        if user.get("background"):
            embed.set_image(url=user["background"])

        embed.set_thumbnail(url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="setbackground", description="Set profile background")
    async def setbackground(self, interaction: discord.Interaction, url: str):

        if not url.startswith("http"):
            return await interaction.response.send_message("Invalid URL.", ephemeral=True)

        await UserModel.update(interaction.user.id, interaction.guild.id, {"background": url})
        await interaction.response.send_message("Background updated.")

    # ==========================================
    # INVENTORY
    # ==========================================

    @app_commands.command(name="inventory", description="View your shadows")
    async def inventory(self, interaction: discord.Interaction):

        user = await UserModel.get(interaction.user.id, interaction.guild.id)
        shadows = user.get("shadows", [])

        if not shadows:
            return await interaction.response.send_message("You own no shadows.")

        shadow_list = {}
        for s in shadows:
            shadow_list[s] = shadow_list.get(s, 0) + 1

        desc = "\n".join([f"{name} x{count}" for name, count in shadow_list.items()])

        embed = discord.Embed(
            title=f"{interaction.user.display_name}'s Shadows",
            description=desc,
            color=discord.Color.dark_purple()
        )

        await interaction.response.send_message(embed=embed)

    # ==========================================
    # LEADERBOARD
    # ==========================================

    @app_commands.command(name="leaderboard", description="Top hunters")
    async def leaderboard(self, interaction: discord.Interaction):

        top_users = await UserModel.leaderboard(interaction.guild.id)

        if not top_users:
            return await interaction.response.send_message("No data.")

        desc = ""
        for i, user in enumerate(top_users, start=1):
            member = interaction.guild.get_member(user["user_id"])
            name = member.display_name if member else "Unknown"
            desc += f"**{i}.** {name} — Level {user['level']}\n"

        embed = discord.Embed(
            title="Hunter Leaderboard",
            description=desc,
            color=discord.Color.gold()
        )

        await interaction.response.send_message(embed=embed)
