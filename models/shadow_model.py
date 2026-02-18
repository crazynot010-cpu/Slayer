from database import shadows


class ShadowModel:

    @staticmethod
    async def create(name: str, rarity: str, spawn_chance: float, image: str):
        shadow = {
            "name": name.lower(),
            "rarity": rarity,
            "spawn_chance": spawn_chance,
            "image": image,
            "stats": {
                "def": 0,
                "dmg": 0,
                "stm": 0
            }
        }
        await shadows.insert_one(shadow)

    @staticmethod
    async def delete(name: str):
        await shadows.delete_one({"name": name.lower()})

    @staticmethod
    async def get(name: str):
        return await shadows.find_one({"name": name.lower()})

    @staticmethod
    async def update_stats(name: str, def_stat: int, dmg: int, stm: int):
        await shadows.update_one(
            {"name": name.lower()},
            {
                "$set": {
                    "stats.def": def_stat,
                    "stats.dmg": dmg,
                    "stats.stm": stm
                }
            }
        )

    @staticmethod
    async def get_all():
        return await shadows.find().to_list(length=None)
