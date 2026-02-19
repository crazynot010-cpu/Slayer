import discord
from discord import app_commands
from discord.ext import commands

from models.user_model import UserModel
from models.guild_model import GuildModel
from models.shadow_model import ShadowModel

from systems.spawn_system import spawn_system
from systems.rank_system import RankSystem


class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # -------------------------
    # SET SPAWN CHANNEL
    # -------------------------

    @app_commands.command(
        name="setspawn",
        description="Set the channel where shadows spawn"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def set_spawn(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):
        await GuildModel.update_guild(
            interaction.guild.id,
            {"spawn_channel_id": channel.id}
        )

        await interaction.response.send_message(
            f"✅ Spawn channel set to {channel.mention}"
        )

    # -------------------------
    # SET PING ROLE
    # -------------------------

    @app_commands.command(
        name="setping",
        description="Set role to ping when shadow spawns"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def set_ping(
        self,
        interaction: discord.Interaction,
        role: discord.Role
    ):
        await GuildModel.update_guild(
            interaction.guild.id,
            {"ping_role_id": role.id}
        )

        await interaction.response.send_message(
            f"✅ Spawn ping role set to {role.mention}"
        )

    # -------------------------
    # ADD SHADOW
    # -------------------------

    @app_commands.command(
        name="addshadow",
        description="Add a new shadow to the database"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def add_shadow(
        self,
        interaction: discord.Interaction,
        name: str,
        rarity: str,
        spawn_chance: app_commands.Range[int, 1, 100],
        hp: int,
        stm: int,
        attack: int,
        image_url: str
    ):
        name = name.lower()

        if not RankSystem.is_valid_rank(rarity):
            await interaction.response.send_message(
                "❌ Invalid rarity. Use: E, D, C, B, A, S, SS, SSS",
                ephemeral=True
            )
            return

        shadow = await ShadowModel.add_shadow(
            name=name,
            rarity=rarity.upper(),
            spawn_chance=spawn_chance,
            hp=hp,
            stm=stm,
            attack=attack,
            image_url=image_url  # FIXED TYPO
        )

        if not shadow:
            await interaction.response.send_message(
                "❌ Shadow already exists.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"✅ Shadow **{name}** added successfully."
        )

    # -------------------------
    # REMOVE SHADOW
    # -------------------------

    @app_commands.command(
        name="removeshadow",
        description="Remove a shadow from the database and all inventories"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_shadow(
        self,
        interaction: discord.Interaction,
        name: str
    ):
        name = name.lower()

        # Remove from shadow database
        removed = await ShadowModel.remove_shadow(name)

        if not removed:
            await interaction.response.send_message(
                "❌ Shadow not found.",
                ephemeral=True
            )
            return

        # Remove from all user inventories
        await UserModel.collection.update_many(
            {},
            {
                "$pull": {
                    "shadows": {"name": name}
                }
            }
        )

        # Remove active spawn if currently spawned
        active = spawn_system.active_spawns.get(interaction.guild.id)

        if active and active["name"].lower() == name:
            del spawn_system.active_spawns[interaction.guild.id]

        await interaction.response.send_message(
            f"🗑️ Shadow **{name}** removed from database and all inventories."
        )


async def setup(bot):
    await bot.add_cog(Admin(bot))
