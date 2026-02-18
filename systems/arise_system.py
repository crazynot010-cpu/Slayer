import random
from models.user_model import UserModel
from systems.spawn_system import spawn_system
from systems.xp_system import XPSystem


class AriseSystem:

    @staticmethod
    async def attempt_arise(user, guild):
        active = spawn_system.active_spawns.get(guild.id)

        if not active:
            return "no_spawn", None

        return "spawn_exists", active

    @staticmethod
    async def resolve_arise(user, guild, guess: str):
        active = spawn_system.active_spawns.get(guild.id)

        if not active:
            return "no_spawn", None

        if guess.lower() != active["name"]:
            return "wrong_guess", None

        success = random.randint(1, 100) <= 55

        del spawn_system.active_spawns[guild.id]

        if not success:
            return "failed", active

        user_data = await UserModel.get_user(user.id, guild.id)

        count = sum(
            1 for s in user_data["shadows"]
            if s["name"] == active["name"]
        )

        if count >= 3:
            return "max_dupe", active

        user_data["shadows"].append({
            "name": active["name"],
            "rarity": active["rarity"],
            "hp": active["hp"],
            "defense": active["defense"],
            "attack": active["attack"]
        })

        await UserModel.update_user(
            user.id,
            guild.id,
            {"shadows": user_data["shadows"]}
        )

        await XPSystem.add_xp(user.id, guild.id, 50)

        return "success", active
