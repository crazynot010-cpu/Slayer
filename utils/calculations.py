import math

def xp_required(level: int) -> int:
    return int(100 * (level ** 1.8))

def calculate_level_from_xp(total_xp: int):
    level = 1
    while total_xp >= xp_required(level):
        total_xp -= xp_required(level)
        level += 1
    return level, total_xp

def calculate_shadow_power(shadow: dict):
    base = shadow["base_power"]
    level = shadow.get("level", 1)
    trait = shadow.get("trait", None)

    power = base + (level * 15)

    trait_multiplier = {
        "Berserker": 1.2,
        "Tank": 1.15,
        "Assassin": 1.25,
        "Arcane": 1.1,
        "Dominator": 1.3
    }

    if trait in trait_multiplier:
        power *= trait_multiplier[trait]

    return int(power)
