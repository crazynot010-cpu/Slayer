def default_player(user_id: int):
    return {
        "_id": user_id,
        "level": 1,
        "xp": 0,
        "hp": 100,
        "max_hp": 100,
        "attack": 10,
        "defense": 5,
        "money": 0,
        "inventory": [],
        "equipped": {
            "weapon": None,
            "armor": None,
            "accessory": None
        }
    }
