from database import users_collection


class UserModel:

    @staticmethod
    async def get_user(user_id: int, guild_id: int):
        user = await users_collection.find_one({
            "user_id": user_id,
            "guild_id": guild_id
        })

        if not user:
            user = {
                "user_id": user_id,
                "guild_id": guild_id,
                "xp": 0,
                "level": 1,
                "shadows": [],
                "background": None
            }
            await users_collection.insert_one(user)

        return user

    @staticmethod
    async def update_user(user_id: int, guild_id: int, data: dict):
        await users_collection.update_one(
            {
                "user_id": user_id,
                "guild_id": guild_id
            },
            {"$set": data},
            upsert=True
        )
