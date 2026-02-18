from models.guild_model import GuildModel
from models.user_model import UserModel
from systems.spawn_system import SpawnSystem
from systems.xp_system import XPSystem


ARISE_XP_REWARD = 25


class AriseSystem:

    @staticmethod
    async def attempt(user_id: int, guild_id: int, guess_name: str):

        guild = await GuildModel.get(guild_id)
        active = guild.get("active_spawn")

        if not active:
            return {"success": False, "reason": "no_spawn"}

        if active.lower() != guess_name.lower():
            return {"success": False, "reason": "wrong_name"}

        added = await UserModel.add_shadow(user_id, guild_id, active)

        if not added:
            return {"success": False, "reason": "max_dupe"}

        await XPSystem.add_xp(user_id, guild_id, ARISE_XP_REWARD)

        await SpawnSystem.clear_spawn(guild_id)

        return {
            "success": True,
            "shadow": active
        }
