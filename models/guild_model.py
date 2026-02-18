from database import guilds_collection


class GuildModel:

    @staticmethod
    async def get_guild(guild_id: int):
        guild = await guilds_collection.find_one({"_id": guild_id})

        if not guild:
            guild = {
                "_id": guild_id,
                "spawn_channel": None,
                "xp_multiplier": 1.0
            }
            await guilds_collection.insert_one(guild)

        return guild

    @staticmethod
    async def set_spawn_channel(guild_id: int, channel_id: int):
        await guilds_collection.update_one(
            {"_id": guild_id},
            {"$set": {"spawn_channel": channel_id}}
        )

    @staticmethod
    async def set_xp_multiplier(guild_id: int, multiplier: float):
        await guilds_collection.update_one(
            {"_id": guild_id},
            {"$set": {"xp_multiplier": multiplier}}
        )
