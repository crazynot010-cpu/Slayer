import discord
from discord.ext import commands
from discord import app_commands
from core.database import users
from core.helpers import xp_needed
from PIL import Image, ImageDraw
import io

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def generate_profile(self, member, data):
        img = Image.new("RGB", (800, 300), (25, 25, 25))
        draw = ImageDraw.Draw(img)

        level = data["level"]
        xp = data["xp"]
        needed = xp_needed(level)

        bar_width = int((xp / needed) * 500)

        draw.rectangle((150, 200, 650, 230), fill=(60,60,60))
        draw.rectangle((150, 200, 150+bar_width, 230), fill=(140,0,255))

        draw.text((150, 50), member.name, fill="white")
        draw.text((150, 100), f"Level: {level}", fill="white")
        draw.text((150, 130), f"Rank: {data['rank']}", fill="white")
        draw.text((150, 160), f"XP: {xp}/{needed}", fill="white")

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer

    @app_commands.command(name="profile")
    async def profile_slash(self, interaction: discord.Interaction):
        data = users.find_one({"user_id": interaction.user.id, "guild_id": interaction.guild.id})
        if not data:
            return await interaction.response.send_message("No data yet.", ephemeral=True)

        img = self.generate_profile(interaction.user, data)
        await interaction.response.send_message(file=discord.File(img, "profile.png"))

    @commands.command(name="profile")
    async def profile_prefix(self, ctx):
        data = users.find_one({"user_id": ctx.author.id, "guild_id": ctx.guild.id})
        if not data:
            return await ctx.send("No data yet.")

        img = self.generate_profile(ctx.author, data)
        await ctx.send(file=discord.File(img, "profile.png"))

    @app_commands.command(name="leaderboard")
    async def leaderboard_slash(self, interaction: discord.Interaction):
        top = users.find({"guild_id": interaction.guild.id}).sort("level", -1).limit(10)
        desc = ""

        for i, user in enumerate(top, 1):
            member = interaction.guild.get_member(user["user_id"])
            if member:
                desc += f"{i}. {member.name} - Level {user['level']}\n"

        embed = discord.Embed(title="Leaderboard", description=desc)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Profile(bot))
