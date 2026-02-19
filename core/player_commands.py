from discord.ext import commands
import discord

from systems.player_system import PlayerSystem
from systems.xp_system import XPSystem
from systems.combat_system import CombatSystem
from utils.embeds import success_embed


class PlayerCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # -------------------------
    # PROFILE
    # -------------------------
    @commands.command()
    async def profile(self, ctx):
        player = await PlayerSystem.get_player(ctx.author.id)

        embed = discord.Embed(
            title=f"{ctx.author.name}'s Profile",
            color=0x3498db
        )

        embed.add_field(name="Level", value=player["level"])
        embed.add_field(name="XP", value=player["xp"])
        embed.add_field(name="HP", value=f"{player['hp']}/{player['max_hp']}")
        embed.add_field(name="Attack", value=player["attack"])
        embed.add_field(name="Defense", value=player["defense"])
        embed.add_field(name="Money", value=player["money"])

        await ctx.send(embed=embed)

    # -------------------------
    # TRAIN
    # -------------------------
    @commands.command()
    async def train(self, ctx):
        await PlayerSystem.add_xp(ctx.author.id, 50)

        player = await PlayerSystem.get_player(ctx.author.id)
        leveled, level = await XPSystem.check_level_up(player)

        if leveled:
            await ctx.send(embed=success_embed(
                "LEVEL UP!",
                f"You are now Level {level}!"
            ))
        else:
            await ctx.send(embed=success_embed(
                "Training Complete",
                "You gained 50 XP."
            ))

    # -------------------------
    # FIGHT
    # -------------------------
    @commands.command()
    async def fight(self, ctx, npc: str):
        result = await CombatSystem.start_combat(ctx.author.id, npc)

        if "error" in result:
            await ctx.send(result["error"])
            return

        description = ""

        for entry in result["log"]:
            attacker = "You" if entry["attacker"] == "player" else "Enemy"
            crit_text = " (CRIT!)" if entry["crit"] else ""
            description += f"{attacker} dealt {entry['damage']} damage{crit_text}\n"

        embed = discord.Embed(
            title="⚔️ Combat",
            description=description,
            color=0x9b59b6
        )

        if result["result"] == "win":
            embed.add_field(name="Result", value="You won!")
        elif result["result"] == "lose":
            embed.add_field(name="Result", value="You were defeated.")
        else:
            embed.add_field(
                name="HP",
                value=f"You: {result['player_hp']} | Enemy: {result['npc_hp']}"
            )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(PlayerCommands(bot))
