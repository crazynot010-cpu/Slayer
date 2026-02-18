import motor.motor_asyncio
from settings import MONGO_URI

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)

db = client["solo_leveling"]

guilds = db["guilds"]
users = db["users"]
shadows = db["shadows"]
