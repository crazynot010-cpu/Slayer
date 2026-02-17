import discord
from discord.ext import commands
from discord import app_commands

from database import users, shadows
from utils.calculations import calculate_shadow_power

MAX_DUPES = 3


class ShadowsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_user(self, member):
        return await users.find_one({
            "user_id": member.id,
            "guild_id": member.guild.id
        })

    @commands.command(name="shadowinfo")
    async def shadowinfo_prefix(self, ctx, name: str):
        shadow = await shadows.find_one({"name": name})
        if not shadow:
            return await ctx.send("Shadow not found.")

        owner_count = await users.count_documents(
            {"shadows.name": name}
        )

        embed = discord.Embed(
            title=shadow["name"],
            description=shadow.get("description", "No description."),
            color=0x9b59b6
        )

        embed.add_field(name="Rarity", value=shadow["rarity"])
        embed.add_field(name="Base Power", value=str(shadow["base_power"]))
        embed.add_field(name="Global Owners", value=str(owner_count))

        await ctx.send(embed=embed)

    @app_commands.command(name="shadow_info", description="View shadow info")
    async def shadowinfo_slash(self, interaction: discord.Interaction, name: str):
        shadow = await shadows.find_one({"name": name})
        if not shadow:
            return await interaction.response.send_message("Shadow not found.")

        owner_count = await users.count_documents(
            {"shadows.name": name}
        )

        embed = discord.Embed(
            title=shadow["name"],
            description=shadow.get("description", "No description."),
            color=0x9b59b6
        )

        embed.add_field(name="Rarity", value=shadow["rarity"])
        embed.add_field(name="Base Power", value=str(shadow["base_power"]))
        embed.add_field(name="Global Owners", value=str(owner_count))

        await interaction.response.send_message(embed=embed)

    @commands.command(name="release")
    async def release_prefix(self, ctx, name: str):
        await self.release_shadow(ctx.author, ctx, name)

    @app_commands.command(name="release", description="Release a shadow")
    async def release_slash(self, interaction: discord.Interaction, name: str):
        await self.release_shadow(interaction.user, interaction, name)

    async def release_shadow(self, member, ctx_or_interaction, name):
        user = await self.get_user(member)
        if not user:
            return

        for shadow in user["shadows"]:
            if shadow["name"] == name:
                await users.update_one(
                    {"_id": user["_id"]},
                    {"$pull": {"shadows": shadow}}
                )
                message = f"{name} released."
                break
        else:
            message = "You don't own that shadow."

        if isinstance(ctx_or_interaction, commands.Context):
            await ctx_or_interaction.send(message)
        else:
            await ctx_or_interaction.response.send_message(message)

    @commands.command(name="upgrade")
    async def upgrade_prefix(self, ctx, name: str):
        await self.upgrade_shadow(ctx.author, ctx, name)

    @app_commands.command(name="upgrade", description="Upgrade a shadow")
    async def upgrade_slash(self, interaction: discord.Interaction, name: str):
        await self.upgrade_shadow(interaction.user, interaction, name)

    async def upgrade_shadow(self, member, ctx_or_interaction, name):
        user = await self.get_user(member)
        if not user:
            return

        owned = [s for s in user["shadows"] if s["name"] == name]

        if len(owned) < 2:
            message = "You need at least 2 duplicates to upgrade."
        else:
            base_shadow = owned[0]
            base_shadow["level"] += 1

            await users.update_one(
                {"_id": user["_id"]},
                {
                    "$set": {"shadows.$[elem].level": base_shadow["level"]},
                    "$pull": {"shadows": owned[1]}
                },
                array_filters=[{"elem.name": name}]
            )

            message = f"{name} upgraded to level {base_shadow['level']}!"

        if isinstance(ctx_or_interaction, commands.Context):
            await ctx_or_interaction.send(message)
        else:
            await ctx_or_interaction.response.send_message(message)


async def setup(bot):
    await bot.add_cog(ShadowsCog(bot))
