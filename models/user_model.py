from database import users


class UserModel:

    @staticmethod
    async def get(user_id: int, guild_id: int):
        user = await users.find_one({
            "user_id": user_id,
            "guild_id": guild_id
        })

        if not user:
            user = {
                "user_id": user_id,
                "guild_id": guild_id,
                "xp": 0,
                "level": 1,
                "background": None,
                "shadows": []
            }
            await users.insert_one(user)

        return user

    @staticmethod
    async def update(user_id: int, guild_id: int, data: dict):
        await users.update_one(
            {"user_id": user_id, "guild_id": guild_id},
            {"$set": data}
        )

    @staticmethod
    async def add_shadow(user_id: int, guild_id: int, shadow_name: str):
        user = await users.find_one({
            "user_id": user_id,
            "guild_id": guild_id
        })

        shadows = user.get("shadows", [])

        if shadows.count(shadow_name) >= 3:
            return False

        await users.update_one(
            {"user_id": user_id, "guild_id": guild_id},
            {"$push": {"shadows": shadow_name}}
        )

        return True

    @staticmethod
    async def leaderboard(guild_id: int, limit: int = 10):
        return await users.find(
            {"guild_id": guild_id}
        ).sort("level", -1).limit(limit).to_list(length=limit)
