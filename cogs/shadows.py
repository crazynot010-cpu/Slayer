import discord
from discord.ext import commands
from discord import app_commands

from database import users, shadows

MAX_DUPES = 3


class ShadowsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ==============================
    # INTERNAL HELPERS
    # ==============================

    async def get_user(self, member: discord.Member):
        return await users.find_one({
            "user_id": member.id,
            "guild_id": member.guild.id
        })

    # ==============================
    # ADMIN - ADD SHADOW
    # ==============================

    @commands.command(name="addshadow")
    @commands.has_permissions(administrator=True)
    async def addshadow_prefix(self, ctx, name: str, rarity: str,
                               spawn_rate: int, hp: int,
                               dmg: int, stm: int, image_url: str):

        existing = await shadows.find_one({"name": name})
        if existing:
            return await ctx.send("❌ Shadow already exists.")

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

        await ctx.send(f"✅ Shadow '{name}' added successfully.")

    @app_commands.command(name="addshadow", description="Add a new shadow")
    @app_commands.checks.has_permissions(administrator=True)
    async def addshadow_slash(self, interaction: discord.Interaction,
                              name: str, rarity: str,
                              spawn_rate: int, hp: int,
                              dmg: int, stm: int,
                              image_url: str):

        existing = await shadows.find_one({"name": name})
        if existing:
            return await interaction.response.send_message(
                "❌ Shadow already exists.", ephemeral=True
            )

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

        await interaction.response.send_message(
            f"✅ Shadow '{name}' added successfully."
        )

    # ==============================
    # ADMIN - REMOVE SHADOW
    # ==============================

    @commands.command(name="removeshadow")
    @commands.has_permissions(administrator=True)
    async def removeshadow_prefix(self, ctx, name: str):
        result = await shadows.delete_one({"name": name})

        if result.deleted_count == 0:
            return await ctx.send("❌ Shadow not found.")

        await ctx.send(f"🗑️ Shadow '{name}' removed.")

    @app_commands.command(name="removeshadow", description="Remove a shadow")
    @app_commands.checks.has_permissions(administrator=True)
    async def removeshadow_slash(self, interaction: discord.Interaction, name: str):

        result = await shadows.delete_one({"name": name})

        if result.deleted_count == 0:
            return await interaction.response.send_message(
                "❌ Shadow not found.", ephemeral=True
            )

        await interaction.response.send_message(
            f"🗑️ Shadow '{name}' removed."
        )

    # ==============================
    # SHADOW INFO
    # ==============================

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
            color=0x9b59b6
        )

        embed.add_field(name="Rarity", value=shadow["rarity"])
        embed.add_field(name="HP", value=str(shadow["hp"]))
        embed.add_field(name="DMG", value=str(shadow["dmg"]))
        embed.add_field(name="STM", value=str(shadow["stm"]))
        embed.add_field(name="Spawn Rate", value=str(shadow["spawn_rate"]))
        embed.add_field(name="Global Owners", value=str(owner_count))

        embed.set_image(url=shadow["image_url"])

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
            color=0x9b59b6
        )

        embed.add_field(name="Rarity", value=shadow["rarity"])
        embed.add_field(name="HP", value=str(shadow["hp"]))
        embed.add_field(name="DMG", value=str(shadow["dmg"]))
        embed.add_field(name="STM", value=str(shadow["stm"]))
        embed.add_field(name="Spawn Rate", value=str(shadow["spawn_rate"]))
        embed.add_field(name="Global Owners", value=str(owner_count))

        embed.set_image(url=shadow["image_url"])

        await interaction.response.send_message(embed=embed)

    # ==============================
    # RELEASE SHADOW
    # ==============================

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

        for shadow in user.get("shadows", []):
            if shadow["name"].lower() == name.lower():
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

    # ==============================
    # UPGRADE SHADOW
    # ==============================

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

        owned = [s for s in user.get("shadows", []) if s["name"].lower() == name.lower()]

        if len(owned) < 2:
            message = "You need at least 2 duplicates to upgrade."
        else:
            new_level = owned[0].get("level", 1) + 1

            await users.update_one(
                {"_id": user["_id"]},
                {
                    "$set": {"shadows.$[elem].level": new_level},
                    "$pull": {"shadows": owned[1]}
                },
                array_filters=[{"elem.name": owned[0]["name"]}]
            )

            message = f"{name} upgraded to level {new_level}!"

        if isinstance(ctx_or_interaction, commands.Context):
            await ctx_or_interaction.send(message)
        else:
            await ctx_or_interaction.response.send_message(message)


async def setup(bot):
    await bot.add_cog(ShadowsCog(bot))
