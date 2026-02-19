import discord
from discord import app_commands
from discord.ext import commands

class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

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
            "money_drop": 0,
            "xp_drop": 0,
            "mastery_drop": 0,
            "moves": []
        })

        embed = discord.Embed(
            title="NPC Created",
            description=f"**{name}** successfully created.",
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
        await self.db.npcs.update_one(
            {"name": npc_name},
            {"$addToSet": {"spawn_channels": channel.id}}
        )

        await interaction.response.send_message(
            f"{channel.mention} added as spawn channel for {npc_name}"
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
            f"Move **{move_name}** added to {npc_name}"
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
            f"Money drop for {npc_name} set to {amount}"
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
            f"Money drop removed for {npc_name}"
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
            f"XP drop for {npc_name} set to {amount}"
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
            f"Mastery drop for {npc_name} set to {amount}"
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
            f"{name} buy requirement updated."
        )

    # =====================================================
    # PERMANENT MASTERY REQUIREMENT
    # =====================================================

    @app_commands.command(name="setmastery")
    async def setmastery(
        self,
        interaction: discord.Interaction,
        category: str,  # weapon / technique / fighting
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
            f"Mastery requirement set for {skill_name}"
        )


async def setup(bot):
    await bot.add_cog(Admin(bot))
