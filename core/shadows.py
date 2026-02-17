from config import MAX_SLOTS, MAX_DUPE
from database.mongo import users

def can_claim(user_data, shadow):
    if len(user_data["shadows"]) >= MAX_SLOTS:
        return False, "Max slots reached."

    if user_data["shadows"].count(shadow) >= MAX_DUPE:
        return False, "Max duplicates reached."

    return True, None

async def add_shadow(user_data, shadow, power):
    user_data["shadows"].append(shadow)
    user_data["total_power"] += power

    await users.update_one(
        {"user_id": user_data["user_id"]},
        {"$set": user_data}
    )
