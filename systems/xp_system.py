from models.user_model import UserModel
from systems.rank_system import RankSystem


class XPSystem:

    @staticmethod
    def xp_required_for_level(level: int) -> int:
        return 100 * level

    @staticmethod
    async def add_xp(user_id: int, amount: int):
        user = await UserModel.get_user(user_id)

        new_xp = user["xp"] + amount
        level = user["level"]

        required = XPSystem.xp_required_for_level(level)

        while new_xp >= required:
            new_xp -= required
            level += 1
            required = XPSystem.xp_required_for_level(level)

        await UserModel.update_level(user_id, level)
        await UserModel.update_rank(user_id, RankSystem.get_rank(level))

        # Set final XP
        from database import users_collection
        await users_collection.update_one(
            {"_id": user_id},
            {"$set": {"xp": new_xp}}
        )

        return level
