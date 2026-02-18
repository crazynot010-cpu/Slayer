from database import guilds


class GuildModel:

    @staticmethod
    async def get(guild_id: int):
        guild = await guilds.find_one({"guild_id": guild_id})

        if not guild:
            guild = {
                "guild_id": guild_id,
                "message_count": 0,
                "rank_roles": {}
            }
            await guilds.insert_one(guild)

        return guild

    @staticmethod
    async def update(guild_id: int, data: dict):
        await guilds.update_one(
            {"guild_id": guild_id},
            {"$set": data}
        )
