import random


class SpawnSystem:

    MONSTERS = [
        {"name": "Goblin", "xp": 25, "gold": 10},
        {"name": "Orc", "xp": 50, "gold": 25},
        {"name": "Knight", "xp": 100, "gold": 50},
        {"name": "Dragon", "xp": 300, "gold": 150}
    ]

    @staticmethod
    def spawn():
        return random.choice(SpawnSystem.MONSTERS)
