from database import players_collection

class XPSystem:

    @staticmethod
    def xp_needed(level: int):
        return 100 * level

    @staticmethod
    async def check_level_up(player: dict):
        needed = XPSystem.xp_needed(player["level"])
        if player["xp"] >= needed:
            new_level = player["level"] + 1

            await players_collection.update_one(
                {"_id": player["_id"]},
                {
                    "$set": {
                        "level": new_level,
                        "xp": 0,
                        "max_hp": player["max_hp"] + 20,
                        "attack": player["attack"] + 5,
                        "defense": player["defense"] + 3
                    }
                }
            )

            return True, new_level

        return False, player["level"]
