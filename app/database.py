import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Load environment variables from .env file if it exists
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "notes_db")

client = AsyncIOMotorClient(MONGO_URI)
database = client[DATABASE_NAME]
notes_collection = database["notes"]
