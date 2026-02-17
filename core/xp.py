import time
import random
from config import CHAT_COOLDOWN, XP_MIN, XP_MAX, RANK_LEVELS
from database.mongo import users

def required_xp(level):
    return 100 + (level * 20)

def get_rank(level):
    current = "E"
    for lvl, rank in sorted(RANK_LEVELS.items()):
        if level >= lvl:
            current = rank
    return current

async def handle_xp(user_data):
    if time.time() - user_data["last_xp"] < CHAT_COOLDOWN:
        return False

    gain = random.randint(XP_MIN, XP_MAX)
    user_data["xp"] += gain
    user_data["last_xp"] = time.time()

    if user_data["xp"] >= required_xp(user_data["level"]):
        user_data["xp"] = 0
        user_data["level"] += 1
        user_data["rank"] = get_rank(user_data["level"])
        await users.update_one({"user_id": user_data["user_id"]}, {"$set": user_data})
        return True

    await users.update_one({"user_id": user_data["user_id"]}, {"$set": user_data})
    return False
