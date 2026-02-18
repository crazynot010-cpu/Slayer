from motor.motor_asyncio import AsyncIOMotorClient
from settings import MONGO_URI


client = AsyncIOMotorClient(MONGO_URI)

db = client["solo_leveling"]

users_collection = db["users"]
guilds_collection = db["guilds"]
shadows_collection = db["shadows"]
