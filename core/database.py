from pymongo import MongoClient
from core.config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client["solo_leveling"]

users = db["users"]
guilds = db["guilds"]
shadows = db["shadows"]
