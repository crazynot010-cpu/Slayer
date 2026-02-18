from models.user_model import UserModel


async def add_xp(user_id: int, guild_id: int, amount: int):
    await UserModel.add_xp(user_id, guild_id, amount)
