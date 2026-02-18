import discord
from discord import app_commands
from discord.ext import commands

from systems.arise_system import AriseSystem
from systems.cooldown_system import cooldown_system


class Arise(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="arise",
        description="Attempt to arise the active shadow"
    )
    async def arise(
        self,
        interaction: discord.Interaction,
        guess: str
    ):
        await interaction.response.defer()

        # Cooldown (5 seconds)
        if cooldown_system.is_on_cooldown(interaction.user.id, 5):
            await interaction.followup.send(
                "⏳ You're on cooldown.",
                ephemeral=True
            )
            return

        result, shadow = await AriseSystem.resolve_arise(
            interaction.user,
            interaction.guild,
            guess
        )

        # No spawn
        if result == "no_spawn":
            await interaction.followup.send(
                "❌ No active shadow.",
                ephemeral=True
            )
            return

        # Wrong guess
        if result == "wrong_guess":
            await interaction.followup.send(
                "❌ Wrong guess.",
                ephemeral=True
            )
            return

        # Failed arise (45%)
        if result == "failed":
            await interaction.followup.send(
                f"💀 You failed to arise **{shadow['name']}**."
            )
            return

        # Max duplicates
        if result == "max_dupe":
            await interaction.followup.send(
                "⚠️ You already own 3 of this shadow.",
                ephemeral=True
            )
            return

        # Success (55%)
        if result == "success":
            await interaction.followup.send(
                f"🔥 SUCCESS! You have arisen **{shadow['name']}**!"
            )
            return


async def setup(bot):
    await bot.add_cog(Arise(bot))
