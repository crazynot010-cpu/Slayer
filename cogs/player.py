import discord
from discord import app_commands
from discord.ext import commands


class Player(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    # =====================================================
    # ENSURE USER EXISTS
    # =====================================================

    async def ensure_user(self, user_id):

        user = await self.db.users.find_one({"_id": user_id})
        if user:
            return user

        data = {
            "_id": user_id,
            "level": 1,
            "xp": 0,
            "xp_needed": 100,
            "hp": 100,
            "max_hp": 100,
            "ce": 50,
            "max_ce": 50,
            "base_dmg": 10,
            "stat_points": 0,
            "money": 0,
            "inventory": [],
            "equipped": {
                "weapon": None,
                "technique": None,
                "fighting": None
            },
            "mastery": {}
        }

        await self.db.users.insert_one(data)
        return data

    # =====================================================
    # PROFILE
    # =====================================================

    @app_commands.command(name="profile")
    async def profile(self, interaction: discord.Interaction):

        user = await self.ensure_user(interaction.user.id)

        embed = discord.Embed(
            title=f"{interaction.user.name}'s Profile",
            color=discord.Color.blue()
        )

        embed.add_field(name="Level", value=user["level"])
        embed.add_field(name="XP", value=f"{user['xp']} / {user['xp_needed']}")
        embed.add_field(name="HP", value=f"{user['hp']} / {user['max_hp']}")
        embed.add_field(name="CE", value=f"{user['ce']} / {user['max_ce']}")
        embed.add_field(name="Base Damage", value=user["base_dmg"])
        embed.add_field(name="Stat Points", value=user["stat_points"])
        embed.add_field(name="Money", value=user["money"], inline=False)

        await interaction.response.send_message(embed=embed)

    # =====================================================
    # UPGRADE STATS
    # =====================================================

    @app_commands.command(name="upgrade")
    async def upgrade(self, interaction: discord.Interaction, stat: str, amount: int):

        user = await self.ensure_user(interaction.user.id)

        if user["stat_points"] < amount:
            return await interaction.response.send_message(
                "Not enough stat points.", ephemeral=True
            )

        update = {"$inc": {"stat_points": -amount}}

        if stat.lower() == "hp":
            update["$inc"]["max_hp"] = amount * 20
        elif stat.lower() == "ce":
            update["$inc"]["max_ce"] = amount * 10
        elif stat.lower() == "dmg":
            update["$inc"]["base_dmg"] = amount * 5
        else:
            return await interaction.response.send_message(
                "Stat must be hp / ce / dmg",
                ephemeral=True
            )

        await self.db.users.update_one({"_id": interaction.user.id}, update)

        await interaction.response.send_message(
            f"{stat.upper()} upgraded by {amount}"
        )


async def setup(bot):
    await bot.add_cog(Player(bot))
