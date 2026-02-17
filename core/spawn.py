import random
import time
from config import SHADOWS, SPAWN_TIMEOUT
from database.mongo import globals_db

async def create_spawn(guild_id):
    shadow = random.choice(list(SHADOWS.keys()))

    await globals_db.update_one(
        {"guild_id": guild_id},
        {"$set": {
            "shadow": shadow,
            "claimed": False,
            "expires_at": time.time() + SPAWN_TIMEOUT
        }},
        upsert=True
    )

    return shadow
