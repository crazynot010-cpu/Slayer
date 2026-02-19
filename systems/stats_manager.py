from config import (
    STAT_HP_MULTIPLIER,
    STAT_CE_MULTIPLIER,
    STAT_DMG_MULTIPLIER
)


class StatManager:

    @staticmethod
    async def upgrade_stat(db, user_id: int, stat: str, amount: int):

        user = await db.users.find_one({"_id": user_id})

        if user["stat_points"] < amount:
            return False

        update = {"$inc": {"stat_points": -amount}}

        if stat == "hp":
            update["$inc"]["max_hp"] = amount * STAT_HP_MULTIPLIER
        elif stat == "ce":
            update["$inc"]["max_ce"] = amount * STAT_CE_MULTIPLIER
        elif stat == "dmg":
            update["$inc"]["base_dmg"] = amount * STAT_DMG_MULTIPLIER
        else:
            return False

        await db.users.update_one({"_id": user_id}, update)
        return True
