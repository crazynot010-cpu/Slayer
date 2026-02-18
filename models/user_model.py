from database import users_collection
from datetime import datetime


class UserModel:

    @staticmethod
    async def get_user(user_id: int):
        user = await users_collection.find_one({"_id": user_id})

        if not user:
            user = {
                "_id": user_id,
                "xp": 0,
                "level": 1,
                "rank": "E",
                "gold": 0,
                "shadows": [],
                "created_at": datetime.utcnow()
            }
            await users_collection.insert_one(user)

        return user

    @staticmethod
    async def add_xp(user_id: int, amount: int):
        await users_collection.update_one(
            {"_id": user_id},
            {"$inc": {"xp": amount}}
        )

    @staticmethod
    async def update_level(user_id: int, level: int):
        await users_collection.update_one(
            {"_id": user_id},
            {"$set": {"level": level}}
        )

    @staticmethod
    async def update_rank(user_id: int, rank: str):
        await users_collection.update_one(
            {"_id": user_id},
            {"$set": {"rank": rank}}
        )

    @staticmethod
    async def add_gold(user_id: int, amount: int):
        await users_collection.update_one(
            {"_id": user_id},
            {"$inc": {"gold": amount}}
        )

    @staticmethod
    async def add_shadow(user_id: int, shadow_id: str):
        await users_collection.update_one(
            {"_id": user_id},
            {"$push": {"shadows": shadow_id}}
      )
