import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

if not TOKEN:
    raise ValueError("TOKEN environment variable is not set.")

if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is not set.")
