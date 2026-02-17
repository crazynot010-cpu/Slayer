from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI

client = AsyncIOMotorClient(MONGO_URI)

db = client["shadowbot"]

users = db["users"]
guilds = db["guilds"]
shadows = db["shadows"]
global_stats = db["global_stats"]
