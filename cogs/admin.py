import discord
from discord import app_commands
from discord.ext import commands

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ---------------------------
    # PERMISSION CHECK
    # ---------------------------

    async def cog_check(self, interaction: discord.Interaction):
        return interaction.user.guild_permissions.administrator

    # ===========================
    # NPC CREATE
    # ===========================

    @app_commands.command(name="npc", description="Create an NPC")
    async def npc_create(
        self,
        interaction: discord.Interaction,
        boss: bool,
        name: str,
        itemdrops: str,
        dropchance: float,
        imageurl: str
    ):
        await self.bot.db.npcs.insert_one({
            "name": name,
            "boss": boss,
            "item_drops": itemdrops.split(","),
            "drop_chance": dropchance,
            "image_url": imageurl,
            "spawn_channels": [],
            "ping_role": None,
            "money_drop": 0,
            "mastery_drop": 0,
            "auto_spawn": True
        })

        await interaction.response.send_message(
            f"NPC `{name}` created successfully.",
            ephemeral=True
        )

    # ===========================
    # SPAWN CHANNEL
    # ===========================

    @app_commands.command(name="npcspawnchannel")
    async def npc_spawn_channel(
        self,
        interaction: discord.Interaction,
        npcname: str,
        channel: discord.TextChannel
    ):
        await self.bot.db.npcs.update_one(
            {"name": npcname},
            {"$addToSet": {"spawn_channels": channel.id}}
        )

        await interaction.response.send_message("Spawn channel added.", ephemeral=True)

    @app_commands.command(name="removenpcfromchannel")
    async def remove_spawn_channel(
        self,
        interaction: discord.Interaction,
        npcname: str,
        channel: discord.TextChannel
    ):
        await self.bot.db.npcs.update_one(
            {"name": npcname},
            {"$pull": {"spawn_channels": channel.id}}
        )

        await interaction.response.send_message("Spawn channel removed.", ephemeral=True)

    # ===========================
    # SET PING ROLE
    # ===========================

    @app_commands.command(name="setpingrole")
    async def set_ping_role(
        self,
        interaction: discord.Interaction,
        npcname: str,
        role: discord.Role
    ):
        await self.bot.db.npcs.update_one(
            {"name": npcname},
            {"$set": {"ping_role": role.id}}
        )

        await interaction.response.send_message("Ping role set.", ephemeral=True)

    @app_commands.command(name="removeping")
    async def remove_ping(
        self,
        interaction: discord.Interaction,
        npcname: str
    ):
        await self.bot.db.npcs.update_one(
            {"name": npcname},
            {"$set": {"ping_role": None}}
        )

        await interaction.response.send_message("Ping removed.", ephemeral=True)

    # ===========================
    # ITEM CREATE
    # ===========================

    @app_commands.command(name="itemcreate")
    async def item_create(
        self,
        interaction: discord.Interaction,
        name: str,
        weapon: bool,
        damage: int,
        grade: str
    ):
        await self.bot.db.items.insert_one({
            "name": name,
            "weapon": weapon,
            "damage": damage if weapon else 0,
            "grade": grade,
            "skills": [],
            "buffs": {}
        })

        await interaction.response.send_message("Item created.", ephemeral=True)

    @app_commands.command(name="itemremove")
    async def item_remove(self, interaction: discord.Interaction, name: str):
        await self.bot.db.items.delete_one({"name": name})
        await interaction.response.send_message("Item removed.", ephemeral=True)

    # ===========================
    # TECHNIQUE CREATE
    # ===========================

    @app_commands.command(name="techniquecreate")
    async def technique_create(
        self,
        interaction: discord.Interaction,
        name: str,
        stockchance: float
    ):
        await self.bot.db.techniques.insert_one({
            "name": name,
            "stock_chance": stockchance,
            "skills": [],
            "buffs": {},
            "domain": None
        })

        await interaction.response.send_message("Technique created.", ephemeral=True)

    @app_commands.command(name="technremove")
    async def technique_remove(self, interaction: discord.Interaction, name: str):
        await self.bot.db.techniques.delete_one({"name": name})
        await interaction.response.send_message("Technique removed.", ephemeral=True)

    # ===========================
    # DOMAIN SET
    # ===========================

    @app_commands.command(name="domainset")
    async def domain_set(
        self,
        interaction: discord.Interaction,
        techniquename: str,
        name: str,
        hpbuff: int,
        dmgbuff: int,
        cebuff: int
    ):
        await self.bot.db.techniques.update_one(
            {"name": techniquename},
            {"$set": {
                "domain": {
                    "name": name,
                    "hp_buff": hpbuff,
                    "dmg_buff": dmgbuff,
                    "ce_buff": cebuff
                }
            }}
        )

        await interaction.response.send_message("Domain set.", ephemeral=True)

    # ===========================
    # MONEY DROP
    # ===========================

    @app_commands.command(name="setmoneydrop")
    async def set_money_drop(
        self,
        interaction: discord.Interaction,
        npcname: str,
        amount: int
    ):
        await self.bot.db.npcs.update_one(
            {"name": npcname},
            {"$set": {"money_drop": amount}}
        )

        await interaction.response.send_message("Money drop set.", ephemeral=True)

    # ===========================
    # MASTERY DROP
    # ===========================

    @app_commands.command(name="masterydrop")
    async def mastery_drop(
        self,
        interaction: discord.Interaction,
        npcname: str,
        amount: int
    ):
        await self.bot.db.npcs.update_one(
            {"name": npcname},
            {"$set": {"mastery_drop": amount}}
        )

        await interaction.response.send_message("Mastery drop set.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Admin(bot))
