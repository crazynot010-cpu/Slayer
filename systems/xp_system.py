from models.user_model import UserModel
from systems.rank_system import RankSystem


class XPSystem:

    @staticmethod
    def xp_required(level: int):
        return 100 * level

    @staticmethod
    async def add_xp(user_id: int, guild_id: int, amount: int, member=None):

        user = await UserModel.get(user_id, guild_id)

        xp = user["xp"] + amount
        level = user["level"]

        leveled_up = False

        while xp >= XPSystem.xp_required(level):
            xp -= XPSystem.xp_required(level)
            level += 1
            leveled_up = True

        await UserModel.update(user_id, guild_id, {
            "xp": xp,
            "level": level
        })

        if leveled_up and member:
            await RankSystem.update_roles(member, level)

        return leveled_up
