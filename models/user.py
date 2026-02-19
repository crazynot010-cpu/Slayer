from config import BASE_HP, BASE_CE, BASE_DAMAGE, LEVEL_BASE_XP


class UserModel:

    @staticmethod
    def create(user_id: int):
        return {
            "_id": user_id,
            "level": 1,
            "xp": 0,
            "xp_needed": LEVEL_BASE_XP,
            "hp": BASE_HP,
            "max_hp": BASE_HP,
            "ce": BASE_CE,
            "max_ce": BASE_CE,
            "base_dmg": BASE_DAMAGE,
            "stat_points": 0,
            "money": 0,
            "inventory": [],
            "equipped": {
                "weapon": None,
                "technique": None,
                "fighting": None,
                "accessory": None
            },
            "mastery": {},
            "clan": None,
            "binding_vows": []
        }
