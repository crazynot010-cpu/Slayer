import random
import discord

from models.guild_model import GuildModel
from models.shadow_model import ShadowModel


class SpawnSystem:

    def __init__(self):
        self.active_spawns = {}

    async def process_message(self, message: discord.Message):
        if message.author.bot:
            return

        guild = await GuildModel.get_guild(message.guild.id)

        if not guild["spawn_channel_id"]:
            return

        if message.channel.id != guild["spawn_channel_id"]:
            return

        count = guild["message_count"] + 1

        if guild["spawn_threshold"] == 0:
            threshold = random.randint(12, 30)
        else:
            threshold = guild["spawn_threshold"]

        if count >= threshold:
            await self.spawn_shadow(message.channel, message.guild)
            count = 0
            threshold = random.randint(12, 30)

        await GuildModel.update_guild(
            message.guild.id,
            {
                "message_count": count,
                "spawn_threshold": threshold
            }
        )

    async def spawn_shadow(self, channel, guild):
        shadow = await ShadowModel.get_weighted_random_shadow()

        if not shadow:
            return

        self.active_spawns[guild.id] = shadow

        embed = discord.Embed(
            title="⚔️ A Shadow Has Appeared!",
            description="Use `/arise <name>` to claim it.",
            color=0x2f3136
        )

        embed.set_image(url=shadow["image_url"])

        guild_data = await GuildModel.get_guild(guild.id)

        ping = ""
        if guild_data["ping_role_id"]:
            role = guild.get_role(guild_data["ping_role_id"])
            if role:
                ping = role.mention

        await channel.send(content=ping, embed=embed)


spawn_system = SpawnSystem()
