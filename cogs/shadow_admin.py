import discord
from discord.ext import commands
from discord import app_commands

from database import shadows


class ShadowAdmin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =========================
    # ADD SHADOW
    # =========================

    async def add_shadow_logic(self, ctx, name, rarity, spawn_rate, hp, dmg, stm, image_url, slash=False):
        name = name.strip()

        existing = await shadows.find_one({"name": name})
        if existing:
            msg = f"❌ Shadow '{name}' already exists."
            if slash:
                return await ctx.response.send_message(msg, ephemeral=True)
            return await ctx.send(msg)

        await shadows.insert_one({
            "name": name,
            "rarity": rarity.upper(),
            "spawn_rate": spawn_rate,
            "hp": hp,
            "dmg": dmg,
            "stm": stm,
            "image_url": image_url,
            "enabled": True
        })

        embed = discord.Embed(
            title="Shadow Added",
            color=discord.Color.dark_purple()
        )
        embed.add_field(name="Name", value=name)
        embed.add_field(name="Rarity", value=rarity.upper())
        embed.add_field(name="Spawn Rate", value=spawn_rate)
        embed.set_image(url=image_url)

        if slash:
            await ctx.response.send_message(embed=embed)
        else:
            await ctx.send(embed=embed)

    @commands.command(name="addshadow")
    @commands.has_permissions(administrator=True)
    async def addshadow_prefix(self, ctx, name: str, rarity: str, spawn_rate: int, hp: int, dmg: int, stm: int, image_url: str):
        await self.add_shadow_logic(ctx, name, rarity, spawn_rate, hp, dmg, stm, image_url)

    @app_commands.command(name="addshadow", description="Add a new shadow")
    @app_commands.checks.has_permissions(administrator=True)
    async def addshadow_slash(self, interaction: discord.Interaction, name: str, rarity: str,
                              spawn_rate: int, hp: int, dmg: int, stm: int, image_url: str):
        await self.add_shadow_logic(interaction, name, rarity, spawn_rate, hp, dmg, stm, image_url, slash=True)

    # =========================
    # REMOVE SHADOW
    # =========================

    async def remove_shadow_logic(self, ctx, name, slash=False):
        result = await shadows.delete_one({"name": name})

        if result.deleted_count == 0:
            msg = f"❌ Shadow '{name}' not found."
        else:
            msg = f"✅ Shadow '{name}' removed."

        if slash:
            await ctx.response.send_message(msg)
        else:
            await ctx.send(msg)

    @commands.command(name="removeshadow")
    @commands.has_permissions(administrator=True)
    async def removeshadow_prefix(self, ctx, name: str):
        await self.remove_shadow_logic(ctx, name)

    @app_commands.command(name="removeshadow", description="Remove a shadow")
    @app_commands.checks.has_permissions(administrator=True)
    async def removeshadow_slash(self, interaction: discord.Interaction, name: str):
        await self.remove_shadow_logic(interaction, name, slash=True)

    # =========================
    # LIST SHADOWS
    # =========================

    async def list_logic(self, ctx, slash=False):
        all_shadows = await shadows.find({"enabled": True}).to_list(length=None)

        if not all_shadows:
            msg = "No shadows available."
            if slash:
                return await ctx.response.send_message(msg)
            return await ctx.send(msg)

        embed = discord.Embed(
            title="Available Shadows",
            color=discord.Color.blurple()
        )

        for s in all_shadows:
            embed.add_field(
                name=f"{s['name']} ({s['rarity']})",
                value=f"SpawnRate: {s['spawn_rate']} | HP: {s['hp']} | DMG: {s['dmg']}",
                inline=False
            )

        if slash:
            await ctx.response.send_message(embed=embed)
        else:
            await ctx.send(embed=embed)

    @commands.command(name="listshadows")
    async def list_prefix(self, ctx):
        await self.list_logic(ctx)

    @app_commands.command(name="listshadows", description="List all shadows")
    async def list_slash(self, interaction: discord.Interaction):
        await self.list_logic(interaction, slash=True)


async def setup(bot):
    await bot.add_cog(ShadowAdmin(bot))
