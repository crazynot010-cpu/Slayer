from database import players_collection
from models.player_model import default_player

class PlayerSystem:

    @staticmethod
    async def get_player(user_id: int):
        player = await players_collection.find_one({"_id": user_id})
        if not player:
            player = default_player(user_id)
            await players_collection.insert_one(player)
        return player

    @staticmethod
    async def add_xp(user_id: int, amount: int):
        player = await PlayerSystem.get_player(user_id)
        new_xp = player["xp"] + amount

        await players_collection.update_one(
            {"_id": user_id},
            {"$set": {"xp": new_xp}}
        )

        return new_xp
