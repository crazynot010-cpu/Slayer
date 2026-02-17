import random

def generate_spawn_threshold():
    return random.randint(30, 60)

def spawn_chance():
    return random.random() <= 0.43
