from config import LEVEL_XP_SCALING


class LevelingSystem:

    @staticmethod
    async def add_xp(db, user_id: int, amount: int):

        await db.users.update_one(
            {"_id": user_id},
            {"$inc": {"xp": amount}}
        )

        user = await db.users.find_one({"_id": user_id})

        leveled = False

        while user["xp"] >= user["xp_needed"]:
            new_level = user["level"] + 1
            new_needed = int(user["xp_needed"] * LEVEL_XP_SCALING)

            await db.users.update_one(
                {"_id": user_id},
                {
                    "$set": {
                        "level": new_level,
                        "xp_needed": new_needed
                    },
                    "$inc": {
                        "stat_points": 5,
                        "max_hp": 10,
                        "max_ce": 5,
                        "base_dmg": 2
                    }
                }
            )

            user = await db.users.find_one({"_id": user_id})
            leveled = True

        return leveled
