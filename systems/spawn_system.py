import random
from models.guild_model import GuildModel
from models.shadow_model import ShadowModel


SPAWN_MIN = 12
SPAWN_MAX = 24
SPAWN_CHANCE = 0.43


class SpawnSystem:

    @staticmethod
    async def increment_message(guild_id: int):
        guild = await GuildModel.get(guild_id)
        count = guild.get("message_count", 0) + 1
        await GuildModel.update(guild_id, {"message_count": count})
        return count

    @staticmethod
    async def try_spawn(guild_id: int):

        guild = await GuildModel.get(guild_id)

        if guild.get("active_spawn"):
            return None

        count = guild.get("message_count", 0)
        threshold = guild.get("spawn_threshold")

        if not threshold:
            threshold = random.randint(SPAWN_MIN, SPAWN_MAX)
            await GuildModel.update(guild_id, {"spawn_threshold": threshold})

        if count < threshold:
            return None

        await GuildModel.update(guild_id, {"message_count": 0})

        if random.random() > SPAWN_CHANCE:
            return None

        shadows = await ShadowModel.get_all()
        if not shadows:
            return None

        chosen = random.choice(shadows)

        await GuildModel.update(guild_id, {
            "active_spawn": chosen["name"],
            "spawn_threshold": random.randint(SPAWN_MIN, SPAWN_MAX)
        })

        return chosen

    @staticmethod
    async def clear_spawn(guild_id: int):
        await GuildModel.update(guild_id, {"active_spawn": None})
