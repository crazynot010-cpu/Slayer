from models.user_model import UserModel


class XPSystem:

    @staticmethod
    def xp_needed(level: int):
        return 100 + (level * 50)

    @staticmethod
    async def add_xp(user_id: int, guild_id: int, amount: int):
        user = await UserModel.get_user(user_id, guild_id)

        xp = user["xp"] + amount
        level = user["level"]

        while xp >= XPSystem.xp_needed(level):
            xp -= XPSystem.xp_needed(level)
            level += 1

        await UserModel.update_user(
            user_id,
            guild_id,
            {
                "xp": xp,
                "level": level
            }
        )

        return level
