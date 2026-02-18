import discord
from discord.ext import commands
from discord import app_commands

from models.shadow_model import ShadowModel
from models.user_model import UserModel
from systems.spawn_system import SpawnSystem
from systems.arise_system import AriseSystem
from systems.xp_system import XPSystem


XP_PER_MESSAGE = 25


class SoloLevelingBot(commands.Bot):

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix=None,
            intents=intents
        )

    async def setup_hook(self):
        await self.tree.sync()
        print("Slash commands synced.")

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        guild_id = message.guild.id
        user_id = message.author.id

        # Give XP per message
        await XPSystem.add_xp(user_id, guild_id, XP_PER_MESSAGE)

        # Increment message counter
        await SpawnSystem.increment_message(guild_id)

        # Try spawn
        spawn = await SpawnSystem.try_spawn(guild_id)

        if spawn:
            embed = discord.Embed(
                title="A Shadow Has Appeared...",
                description="Use `/arise <name>` to claim it.",
                color=discord.Color.dark_purple()
            )
            embed.set_image(url=spawn["image"])
            await message.channel.send(embed=embed)

    # ===============================
    # SHADOW ADMIN COMMANDS
    # ===============================

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

    # ===============================
    # ARISE
    # ===============================

    @app_commands.command(name="arise", description="Claim the active shadow")
    async def arise(self, interaction: discord.Interaction, name: str):

        result = await AriseSystem.attempt(
            interaction.user.id,
            interaction.guild.id,
            name
        )

        if not result["success"]:
            if result["reason"] == "no_spawn":
                return await interaction.response.send_message("No active shadow.", ephemeral=True)
            if result["reason"] == "wrong_name":
                return await interaction.response.send_message("Wrong name.", ephemeral=True)

        shadow_name = result["shadow"]

        await interaction.response.send_message(
            f"{interaction.user.mention} has arisen **{shadow_name}**!"
        )

    # ===============================
    # VIEW SHADOW
    # ===============================

    @app_commands.command(name="viewshadow", description="View shadow info")
    async def viewshadow(self, interaction: discord.Interaction, name: str):

        shadow = await ShadowModel.get(name)

        if not shadow:
            return await interaction.response.send_message("Shadow not found.", ephemeral=True)

        embed = discord.Embed(
            title=shadow["name"].title(),
            color=discord.Color.dark_purple()
        )

        embed.add_field(name="Rarity", value=shadow["rarity"])
        embed.add_field(name="Damage", value=shadow["stats"]["dmg"])
        embed.add_field(name="Defense", value=shadow["stats"]["def"])
        embed.add_field(name="Stamina", value=shadow["stats"]["stm"])

        embed.set_image(url=shadow["image"])

        await interaction.response.send_message(embed=embed)

    # ===============================
    # PROFILE
    # ===============================

    @app_commands.command(name="profile", description="View your profile")
    async def profile(self, interaction: discord.Interaction):

        user = await UserModel.get(
            interaction.user.id,
            interaction.guild.id
        )

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

    @app_commands.command(name="setbackground", description="Set profile background image")
    async def setbackground(self, interaction: discord.Interaction, url: str):

        if not url.startswith("http"):
            return await interaction.response.send_message("Invalid URL.", ephemeral=True)

        await UserModel.update(
            interaction.user.id,
            interaction.guild.id,
            {"background": url}
        )

        await interaction.response.send_message("Background updated.")
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
