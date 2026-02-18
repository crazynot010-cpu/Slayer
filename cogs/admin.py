import discord
from discord.ext import commands
from discord import app_commands

from models.user_model import UserModel
from systems.spawn_system import SpawnSystem
from utils.embeds import base_embed, error_embed, success_embed


def is_admin():
    async def predicate(ctx_or_interaction):
        user = ctx_or_interaction.user if isinstance(ctx_or_interaction, discord.Interaction) else ctx_or_interaction.author
        return user.guild_permissions.administrator
    return app_commands.check(predicate)


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # -------------------------
    # ADD XP
    # -------------------------

    @commands.command(name="addxp")
    @commands.has_permissions(administrator=True)
    async def addxp_prefix(self, ctx, member: discord.Member, amount: int):
        await self.add_xp_logic(ctx, member, amount)

    @app_commands.command(name="addxp", description="Add XP to a user")
    @app_commands.checks.has_permissions(administrator=True)
    async def addxp_slash(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        await interaction.response.defer()
        await self.add_xp_logic(interaction, member, amount, slash=True)

    async def add_xp_logic(self, ctx_or_interaction, member, amount, slash=False):
        if amount <= 0:
            embed = error_embed("Amount must be positive.")
        else:
            await UserModel.add_xp(member.id, amount)
            embed = success_embed(f"Added {amount} XP to {member.mention}")

        if slash:
            await ctx_or_interaction.followup.send(embed=embed)
        else:
            await ctx_or_interaction.send(embed=embed)

    # -------------------------
    # ADD GOLD
    # -------------------------

    @commands.command(name="addgold")
    @commands.has_permissions(administrator=True)
    async def addgold_prefix(self, ctx, member: discord.Member, amount: int):
        await self.add_gold_logic(ctx, member, amount)

    @app_commands.command(name="addgold", description="Add gold to a user")
    @app_commands.checks.has_permissions(administrator=True)
    async def addgold_slash(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        await interaction.response.defer()
        await self.add_gold_logic(interaction, member, amount, slash=True)

    async def add_gold_logic(self, ctx_or_interaction, member, amount, slash=False):
        if amount <= 0:
            embed = error_embed("Amount must be positive.")
        else:
            await UserModel.add_gold(member.id, amount)
            embed = success_embed(f"Added {amount} gold to {member.mention}")

        if slash:
            await ctx_or_interaction.followup.send(embed=embed)
        else:
            await ctx_or_interaction.send(embed=embed)

    # -------------------------
    # SET LEVEL
    # -------------------------

    @commands.command(name="setlevel")
    @commands.has_permissions(administrator=True)
    async def setlevel_prefix(self, ctx, member: discord.Member, level: int):
        await self.set_level_logic(ctx, member, level)

    @app_commands.command(name="setlevel", description="Set a user's level")
    @app_commands.checks.has_permissions(administrator=True)
    async def setlevel_slash(self, interaction: discord.Interaction, member: discord.Member, level: int):
        await interaction.response.defer()
        await self.set_level_logic(interaction, member, level, slash=True)

    async def set_level_logic(self, ctx_or_interaction, member, level, slash=False):
        if level <= 0:
            embed = error_embed("Level must be greater than 0.")
        else:
            await UserModel.set_level(member.id, level)
            embed = success_embed(f"{member.mention} level set to {level}")

        if slash:
            await ctx_or_interaction.followup.send(embed=embed)
        else:
            await ctx_or_interaction.send(embed=embed)

    # -------------------------
    # FORCE SPAWN
    # -------------------------

    @commands.command(name="forcespawn")
    @commands.has_permissions(administrator=True)
    async def forcespawn_prefix(self, ctx):
        monster = SpawnSystem.spawn_for_channel(ctx.channel.id)
        embed = base_embed(title="Forced Spawn")
        embed.description = f"{monster['name']} has appeared!"
        await ctx.send(embed=embed)

    @app_commands.command(name="forcespawn", description="Force spawn a monster")
    @app_commands.checks.has_permissions(administrator=True)
    async def forcespawn_slash(self, interaction: discord.Interaction):
        monster = SpawnSystem.spawn_for_channel(interaction.channel.id)
        embed = base_embed(title="Forced Spawn")
        embed.description = f"{monster['name']} has appeared!"
        await interaction.response.send_message(embed=embed)

    # -------------------------
    # RESET USER
    # -------------------------

    @commands.command(name="resetuser")
    @commands.has_permissions(administrator=True)
    async def resetuser_prefix(self, ctx, member: discord.Member):
        await UserModel.reset_user(member.id)
        embed = success_embed(f"{member.mention} has been reset.")
        await ctx.send(embed=embed)

    @app_commands.command(name="resetuser", description="Reset a user's data")
    @app_commands.checks.has_permissions(administrator=True)
    async def resetuser_slash(self, interaction: discord.Interaction, member: discord.Member):
        await UserModel.reset_user(member.id)
        embed = success_embed(f"{member.mention} has been reset.")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Admin(bot))
