import discord
from discord.ext import commands
from discord import app_commands

from database import users
from utils.calculations import calculate_shadow_power

MAX_SLOTS = 16


class InventoryCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def build_inventory_embed(self, member: discord.Member):
        user = await users.find_one({
            "user_id": member.id,
            "guild_id": member.guild.id
        })

        if not user or not user["shadows"]:
            return discord.Embed(
                title="Inventory",
                description="You own no shadows.",
                color=0x2c3e50
            )

        shadow_counts = {}
        total_power = 0

        for shadow in user["shadows"]:
            name = shadow["name"]
            shadow_counts[name] = shadow_counts.get(name, 0) + 1
            total_power += calculate_shadow_power(shadow)

        description = ""
        for name, count in shadow_counts.items():
            description += f"**{name}** x{count}\n"

        embed = discord.Embed(
            title=f"{member.display_name}'s Army",
            description=description,
            color=0x8e44ad
        )

        embed.add_field(name="Slots Used", value=f"{len(user['shadows'])}/{MAX_SLOTS}")
        embed.add_field(name="Total Power", value=str(total_power))

        return embed

    @commands.command(name="inventory")
    async def inventory_prefix(self, ctx):
        embed = await self.build_inventory_embed(ctx.author)
        await ctx.send(embed=embed)

    @app_commands.command(name="inventory", description="View your shadow inventory")
    async def inventory_slash(self, interaction: discord.Interaction):
        embed = await self.build_inventory_embed(interaction.user)
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(InventoryCog(bot))
