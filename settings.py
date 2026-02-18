import os

# ==============================
# ENVIRONMENT
# ==============================

TOKEN = os.getenv("TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

# ==============================
# GAME SETTINGS
# ==============================

SPAWN_THRESHOLD = 10
SPAWN_DESPAWN_TIME = 120  # seconds

BASE_SUCCESS_RATE = 0.55

MAX_SHADOW_SLOTS = 16
MAX_DUPLICATES = 3

SUCCESS_XP_REWARD = 50
