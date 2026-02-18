import motor.motor_asyncio
from settings import MONGO_URI

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client["solo_leveling"]

users = db["users"]
guilds = db["guilds"]
shadows = db["shadows"]
