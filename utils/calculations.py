import random
from config import CRIT_CHANCE, CRIT_MULTIPLIER


def calculate_damage(base_damage: int, bonus: int = 0):
    total = base_damage + bonus

    if random.random() < CRIT_CHANCE:
        total = int(total * CRIT_MULTIPLIER)
        return total, True

    return total, False


def calculate_equal_split(total_amount: int, player_count: int):
    if player_count == 0:
        return 0
    return total_amount // player_count
