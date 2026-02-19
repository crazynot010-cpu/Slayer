import discord
import random
from discord import app_commands
from discord.ext import commands


class Raid(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.active_raids = {}  # guild_id: raid_data

    # =====================================================
    # CREATE RAID
    # =====================================================

    @app_commands.command(name="raidcreate")
    async def raidcreate(self, interaction: discord.Interaction, npc_name: str):

        npc = await self.db.npcs.find_one({"name": npc_name})
        if not npc:
            return await interaction.response.send_message("NPC not found.", ephemeral=True)

        guild = interaction.guild

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel = await guild.create_text_channel(
            name=f"raid-{npc_name}",
            overwrites=overwrites
        )

        self.active_raids[guild.id] = {
            "npc": npc,
            "channel_id": channel.id,
            "players": {interaction.user.id: 0},  # damage tracker
            "hp": npc["hp"]
        }

        await interaction.response.send_message(
            f"Raid created: {channel.mention}"
        )

    # =====================================================
    # JOIN RAID
    # =====================================================

    @app_commands.command(name="raidjoin")
    async def raidjoin(self, interaction: discord.Interaction):

        raid = self.active_raids.get(interaction.guild.id)
        if not raid:
            return await interaction.response.send_message("No active raid.", ephemeral=True)

        channel = interaction.guild.get_channel(raid["channel_id"])
        await channel.set_permissions(interaction.user, read_messages=True, send_messages=True)

        raid["players"][interaction.user.id] = 0

        await interaction.response.send_message(
            f"You joined the raid: {channel.mention}"
        )

    # =====================================================
    # LEAVE RAID
    # =====================================================

    @app_commands.command(name="raidleave")
    async def raidleave(self, interaction: discord.Interaction):

        raid = self.active_raids.get(interaction.guild.id)
        if not raid:
            return await interaction.response.send_message("No active raid.", ephemeral=True)

        if interaction.user.id in raid["players"]:
            del raid["players"][interaction.user.id]

        await interaction.response.send_message("You left the raid.")

    # =====================================================
    # START RAID COMBAT
    # =====================================================

    @app_commands.command(name="raidstart")
    async def raidstart(self, interaction: discord.Interaction):

        raid = self.active_raids.get(interaction.guild.id)
        if not raid:
            return await interaction.response.send_message("No active raid.", ephemeral=True)

        channel = interaction.guild.get_channel(raid["channel_id"])
        npc = raid["npc"]

        embed = discord.Embed(
            title=f"{npc['name']} Appeared!",
            description=f"HP: {raid['hp']}",
            color=discord.Color.red()
        )

        if npc["image_url"]:
            embed.set_image(url=npc["image_url"])

        await channel.send(embed=embed)

        # Combat loop (simplified turn-based)
        while raid["hp"] > 0 and raid["players"]:

            await discord.utils.sleep_until(discord.utils.utcnow())

            # Players deal random damage
            for player_id in list(raid["players"].keys()):
                damage = random.randint(50, 150)
                raid["players"][player_id] += damage
                raid["hp"] -= damage

                if raid["hp"] <= 0:
                    break

            # Boss attacks random player
            if raid["hp"] > 0:
                target_id = random.choice(list(raid["players"].keys()))
                move = random.choice(npc["moves"]) if npc["moves"] else None

                if move:
                    dmg = random.randint(move["min"], move["max"])
                else:
                    dmg = random.randint(50, npc["damage"])

                user = interaction.guild.get_member(target_id)

                if dmg > 200:  # simple death threshold
                    await channel.send(f"{user.mention} was defeated!")
                    await channel.set_permissions(user, overwrite=None)
                    del raid["players"][target_id]

        # Raid finished
        if raid["hp"] <= 0:
            await self.distribute_rewards(interaction.guild, raid)

        del self.active_raids[interaction.guild.id]

    # =====================================================
    # REWARD DISTRIBUTION
    # =====================================================

    async def distribute_rewards(self, guild, raid):

        npc = raid["npc"]
        players = raid["players"]

        if not players:
            return

        total_damage = sum(players.values())
        highest_player = max(players, key=players.get)

        money = npc.get("money_drop", 0)
        xp = npc.get("xp_drop", 0)
        mastery = npc.get("mastery_drop", 0)

        equal_money = money // len(players) if players else 0

        for player_id, dmg in players.items():

            bonus = 0
            if player_id == highest_player:
                bonus = int(equal_money * 0.25)

            await self.db.users.update_one(
                {"user_id": player_id},
                {
                    "$inc": {
                        "money": equal_money + bonus,
                        "xp": xp,
                        "mastery": mastery
                    }
                }
            )

        channel = guild.get_channel(raid["channel_id"])
        await channel.send("Raid completed! Rewards distributed.")

        await channel.delete()

async def setup(bot):
    await bot.add_cog(Raid(bot))
