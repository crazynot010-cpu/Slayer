import discord
from discord.ext import commands

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(administrator=True)
    @commands.command(name="resetuser")
    async def reset_user(self, ctx, member: discord.Member):
        await self.bot.db.users.delete_one({"_id": member.id})
        await ctx.send(f"{member.mention} data reset.")

    @discord.app_commands.command(name="resetuser", description="Reset a user's data")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def reset_user_slash(self, interaction: discord.Interaction, member: discord.Member):
        await self.bot.db.users.delete_one({"_id": member.id})
        await interaction.response.send_message(f"{member.mention} data reset.")


async def setup(bot):
    await bot.add_cog(Admin(bot))
