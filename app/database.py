# Authored by Naren Pradhan (https://github.com/Narenpradhan)
# PyNotes: Two-Tier Containerized Application Deployment in Kubernetes

import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument

# Load environment variables from .env file if it exists
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "notes_db")

client = AsyncIOMotorClient(MONGO_URI)
database = client[DATABASE_NAME]
notes_collection = database["notes"]
counters_collection = database["counters"]


async def get_next_note_id() -> str:
    """Generate an atomic 3-digit sequential note ID starting at 101, avoiding duplicates."""
    counter = await counters_collection.find_one_and_update(
        {"_id": "note_id"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    seq = counter.get("seq", 1) if counter else 1
    if seq < 100:
        await counters_collection.update_one({"_id": "note_id"}, {"$set": {"seq": 101}})
        seq = 101

    # Check if a note already exists with this ID (to prevent DuplicateKeyError)
    while await notes_collection.find_one({"_id": str(seq)}):
        seq += 1
        await counters_collection.update_one({"_id": "note_id"}, {"$set": {"seq": seq}})

    return str(seq)
