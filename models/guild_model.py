from database import guilds_collection


class GuildModel:

    @staticmethod
    async def get_guild(guild_id: int):
        guild = await guilds_collection.find_one({"guild_id": guild_id})

        if not guild:
            guild = {
                "guild_id": guild_id,
                "spawn_channel_id": None,
                "ping_role_id": None,
                "message_count": 0,
                "spawn_threshold": 0,
                "active_shadow": None
            }
            await guilds_collection.insert_one(guild)

        return guild

    @staticmethod
    async def update_guild(guild_id: int, data: dict):
        await guilds_collection.update_one(
            {"guild_id": guild_id},
            {"$set": data},
            upsert=True
        )
