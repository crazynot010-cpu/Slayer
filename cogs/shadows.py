import discord
from discord.ext import commands
from discord import app_commands
from core.database import shadows

class Shadows(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =========================
    # ADD SHADOW (ADMIN)
    # =========================

    @app_commands.command(name="addshadow", description="Add a global shadow")
    @app_commands.checks.has_permissions(administrator=True)
    async def addshadow_slash(self, interaction: discord.Interaction,
                              name: str,
                              rarity: str,
                              defense: int,
                              damage: int,
                              stamina: int,
                              spawn_chance: int,
                              image: str):

        if shadows.find_one({"name": name}):
            return await interaction.response.send_message("Shadow already exists.", ephemeral=True)

        shadows.insert_one({
            "name": name,
            "rarity": rarity,
            "def": defense,
            "dmg": damage,
            "stm": stamina,
            "spawn_chance": spawn_chance,
            "image": image
        })

        await interaction.response.send_message(f"{name} added globally.")

    @commands.command(name="addshadow")
    @commands.has_permissions(administrator=True)
    async def addshadow_prefix(self, ctx, name, rarity,
                               defense: int,
                               damage: int,
                               stamina: int,
                               spawn_chance: int,
                               image):

        if shadows.find_one({"name": name}):
            return await ctx.send("Shadow already exists.")

        shadows.insert_one({
            "name": name,
            "rarity": rarity,
            "def": defense,
            "dmg": damage,
            "stm": stamina,
            "spawn_chance": spawn_chance,
            "image": image
        })

        await ctx.send(f"{name} added globally.")

    # =========================
    # REMOVE SHADOW
    # =========================

    @app_commands.command(name="removeshadow", description="Remove a shadow")
    @app_commands.checks.has_permissions(administrator=True)
    async def removeshadow_slash(self, interaction: discord.Interaction, name: str):
        result = shadows.delete_one({"name": name})
        if result.deleted_count == 0:
            return await interaction.response.send_message("Shadow not found.", ephemeral=True)

        await interaction.response.send_message(f"{name} removed.")

    @commands.command(name="removeshadow")
    @commands.has_permissions(administrator=True)
    async def removeshadow_prefix(self, ctx, name):
        result = shadows.delete_one({"name": name})
        if result.deleted_count == 0:
            return await ctx.send("Shadow not found.")

        await ctx.send(f"{name} removed.")

    # =========================
    # SHADOW STATS
    # =========================

    @app_commands.command(name="statsshdw", description="View shadow stats")
    async def statsshdw_slash(self, interaction: discord.Interaction, name: str):
        shadow = shadows.find_one({"name": name})
        if not shadow:
            return await interaction.response.send_message("Shadow not found.", ephemeral=True)

        embed = discord.Embed(
            title=f"{shadow['name']} Stats",
            color=discord.Color.purple()
        )
        embed.add_field(name="Rarity", value=shadow["rarity"])
        embed.add_field(name="DEF", value=shadow["def"])
        embed.add_field(name="DMG", value=shadow["dmg"])
        embed.add_field(name="STM", value=shadow["stm"])
        embed.add_field(name="Spawn Chance", value=f"{shadow['spawn_chance']}%")
        embed.set_image(url=shadow["image"])

        await interaction.response.send_message(embed=embed)

    @commands.command(name="statsshdw")
    async def statsshdw_prefix(self, ctx, name):
        shadow = shadows.find_one({"name": name})
        if not shadow:
            return await ctx.send("Shadow not found.")

        embed = discord.Embed(
            title=f"{shadow['name']} Stats",
            color=discord.Color.purple()
        )
        embed.add_field(name="Rarity", value=shadow["rarity"])
        embed.add_field(name="DEF", value=shadow["def"])
        embed.add_field(name="DMG", value=shadow["dmg"])
        embed.add_field(name="STM", value=shadow["stm"])
        embed.add_field(name="Spawn Chance", value=f"{shadow['spawn_chance']}%")
        embed.set_image(url=shadow["image"])

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Shadows(bot))
