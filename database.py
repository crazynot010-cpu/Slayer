from motor.motor_asyncio import AsyncIOMotorClient
from settings import MONGO_URI

client = AsyncIOMotorClient(MONGO_URI)
db = client["mmorpg_bot"]

players_collection = db["players"]
guilds_collection = db["guilds"]import motor.motor_asyncio
from config import MONGO_URI, DATABASE_NAME


class Database:

    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
        self.db = self.client[DATABASE_NAME]

    def get_db(self):
        return self.db
