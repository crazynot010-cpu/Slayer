from database import shadows_collection
import random


class ShadowModel:

    @staticmethod
    async def add_shadow(
        name: str,
        rarity: str,
        spawn_chance: int,
        hp: int,
        stm: int,
        attack: int,
        image_url: str
    ):
        existing = await shadows_collection.find_one(
            {"name": name.lower()}
        )

        if existing:
            return None

        shadow = {
            "name": name.lower(),
            "rarity": rarity.upper(),
            "spawn_chance": spawn_chance,
            "hp": hp,
            "stm": stm,
            "attack": attack,
            "image_url": image_url
        }

        await shadows_collection.insert_one(shadow)
        return shadow

    @staticmethod
    async def remove_shadow(name: str):
        result = await shadows_collection.delete_one(
            {"name": name.lower()}
        )
        return result.deleted_count > 0

    @staticmethod
    async def get_shadow(name: str):
        return await shadows_collection.find_one(
            {"name": name.lower()}
        )

    @staticmethod
    async def get_weighted_random_shadow():
        shadows = await shadows_collection.find().to_list(length=None)

        if not shadows:
            return None

        weighted_pool = []
        for shadow in shadows:
            weighted_pool.extend([shadow] * shadow["spawn_chance"])

        return random.choice(weighted_pool)
