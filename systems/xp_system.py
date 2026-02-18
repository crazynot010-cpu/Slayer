from models.user_model import UserModel


class XPSystem:

    @staticmethod
    def xp_required(level: int) -> int:
        # Simple scalable formula
        return 100 * level

    @staticmethod
    async def add_xp(user_id: int, guild_id: int, amount: int):
        user = await UserModel.get(user_id, guild_id)

        current_xp = user["xp"]
        current_level = user["level"]

        new_xp = current_xp + amount
        leveled_up = False

        while new_xp >= XPSystem.xp_required(current_level):
            new_xp -= XPSystem.xp_required(current_level)
            current_level += 1
            leveled_up = True

        await UserModel.update(
            user_id,
            guild_id,
            {
                "xp": new_xp,
                "level": current_level
            }
        )

        return {
            "leveled_up": leveled_up,
            "level": current_level,
            "xp": new_xp,
            "xp_needed": XPSystem.xp_required(current_level)
        }
