import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
MONGO_URI = os.getenv("MONGO_URL")

if not TOKEN:
    raise RuntimeError("TOKEN environment variable not set.")

if not MONGO_URI:
    raise RuntimeError("MONGO_URI environment variable not set.")
