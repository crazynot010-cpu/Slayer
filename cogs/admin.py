import discord
from discord import app_commands
from discord.ext import commands


class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    # =====================================================
    # PERMISSION CHECK
    # =====================================================

    async def cog_check(self, interaction: discord.Interaction):
        return interaction.user.guild_permissions.administrator

    # =====================================================
    # CREATE NPC / BOSS
    # =====================================================

    @app_commands.command(name="createnpc", description="Create an NPC or Boss")
    async def createnpc(
        self,
        interaction: discord.Interaction,
        name: str,
        hp: int,
        damage: int,
        boss: bool,
        auto_spawn: bool,
        image_url: str = None
    ):
        existing = await self.db.npcs.find_one({"name": name})
        if existing:
            return await interaction.response.send_message(
                "NPC already exists.", ephemeral=True
            )

        await self.db.npcs.insert_one({
            "name": name,
            "hp": hp,
            "damage": damage,
            "boss": boss,
            "auto_spawn": auto_spawn,
            "image_url": image_url,
            "spawn_channels": [],
            "ping_role": None,
            "money_drop": 0,
            "xp_drop": 0,
            "mastery_drop": 0,
            "moves": []
        })

        embed = discord.Embed(
            title="NPC Created",
            description=f"**{name}** has been successfully created.",
            color=discord.Color.green()
        )

        await interaction.response.send_message(embed=embed)

    # =====================================================
    # ADD SPAWN CHANNEL
    # =====================================================

    @app_commands.command(name="addspawnchannel")
    async def addspawnchannel(
        self,
        interaction: discord.Interaction,
        npc_name: str,
        channel: discord.TextChannel
    ):
        npc = await self.db.npcs.find_one({"name": npc_name})
        if not npc:
            return await interaction.response.send_message("NPC not found.", ephemeral=True)

        await self.db.npcs.update_one(
            {"name": npc_name},
            {"$addToSet": {"spawn_channels": channel.id}}
        )

        await interaction.response.send_message(
            f"{channel.mention} added as spawn channel for **{npc_name}**"
        )

    # =====================================================
    # SET PING ROLE
    # =====================================================

    @app_commands.command(name="setping")
    async def setping(
        self,
        interaction: discord.Interaction,
        npc_name: str,
        role: discord.Role
    ):
        npc = await self.db.npcs.find_one({"name": npc_name})
        if not npc:
            return await interaction.response.send_message("NPC not found.", ephemeral=True)

        await self.db.npcs.update_one(
            {"name": npc_name},
            {"$set": {"ping_role": role.id}}
        )

        embed = discord.Embed(
            title="Ping Role Set",
            description=f"{role.mention} will be pinged when **{npc_name}** spawns.",
            color=discord.Color.blue()
        )

        await interaction.response.send_message(embed=embed)

    # =====================================================
    # REMOVE PING ROLE
    # =====================================================

    @app_commands.command(name="removeping")
    async def removeping(
        self,
        interaction: discord.Interaction,
        npc_name: str
    ):
        await self.db.npcs.update_one(
            {"name": npc_name},
            {"$set": {"ping_role": None}}
        )

        await interaction.response.send_message(
            f"Ping role removed for **{npc_name}**"
        )

    # =====================================================
    # ADD BOSS MOVE
    # =====================================================

    @app_commands.command(name="addmove")
    async def addmove(
        self,
        interaction: discord.Interaction,
        npc_name: str,
        move_name: str,
        min_damage: int,
        max_damage: int
    ):
        npc = await self.db.npcs.find_one({"name": npc_name})
        if not npc:
            return await interaction.response.send_message("NPC not found.", ephemeral=True)

        move_data = {
            "name": move_name,
            "min": min_damage,
            "max": max_damage
        }

        await self.db.npcs.update_one(
            {"name": npc_name},
            {"$push": {"moves": move_data}}
        )

        await interaction.response.send_message(
            f"Move **{move_name}** added to **{npc_name}**"
        )

    # =====================================================
    # MONEY DROP SYSTEM
    # =====================================================

    @app_commands.command(name="setmoneydrop")
    async def setmoneydrop(
        self,
        interaction: discord.Interaction,
        npc_name: str,
        amount: int
    ):
        await self.db.npcs.update_one(
            {"name": npc_name},
            {"$set": {"money_drop": amount}}
        )

        await interaction.response.send_message(
            f"Money drop for **{npc_name}** set to {amount}"
        )

    @app_commands.command(name="removemoneydrop")
    async def removemoneydrop(
        self,
        interaction: discord.Interaction,
        npc_name: str
    ):
        await self.db.npcs.update_one(
            {"name": npc_name},
            {"$set": {"money_drop": 0}}
        )

        await interaction.response.send_message(
            f"Money drop removed for **{npc_name}**"
        )

    # =====================================================
    # XP DROP SYSTEM
    # =====================================================

    @app_commands.command(name="setxpdrop")
    async def setxpdrop(
        self,
        interaction: discord.Interaction,
        npc_name: str,
        amount: int
    ):
        await self.db.npcs.update_one(
            {"name": npc_name},
            {"$set": {"xp_drop": amount}}
        )

        await interaction.response.send_message(
            f"XP drop for **{npc_name}** set to {amount}"
        )

    # =====================================================
    # MASTERY DROP SYSTEM
    # =====================================================

    @app_commands.command(name="masterydrop")
    async def masterydrop(
        self,
        interaction: discord.Interaction,
        npc_name: str,
        amount: int
    ):
        await self.db.npcs.update_one(
            {"name": npc_name},
            {"$set": {"mastery_drop": amount}}
        )

        await interaction.response.send_message(
            f"Mastery drop for **{npc_name}** set to {amount}"
        )

    # =====================================================
    # TECHNIQUE BUY REQUIREMENTS
    # =====================================================

    @app_commands.command(name="settechniquebuy")
    async def settechniquebuy(
        self,
        interaction: discord.Interaction,
        name: str,
        required_money: int,
        required_item: str = None
    ):
        await self.db.techniques.update_one(
            {"name": name},
            {"$set": {
                "price": required_money,
                "required_item": required_item
            }},
            upsert=True
        )

        await interaction.response.send_message(
            f"Technique **{name}** buy requirements updated."
        )

    # =====================================================
    # PERMANENT MASTERY REQUIREMENT
    # =====================================================

    @app_commands.command(name="setmastery")
    async def setmastery(
        self,
        interaction: discord.Interaction,
        category: str,
        skill_name: str,
        mastery_required: int
    ):
        await self.db.mastery.update_one(
            {"skill": skill_name},
            {"$set": {
                "category": category.lower(),
                "required": mastery_required
            }},
            upsert=True
        )

        await interaction.response.send_message(
            f"Mastery requirement set for **{skill_name}**"
        )


async def setup(bot):
    await bot.add_cog(Admin(bot))
