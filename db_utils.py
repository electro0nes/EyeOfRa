from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client['bugbounty']
programs = db['programs']

def insert_or_update_program(platform, handle, name, data):
    programs.update_one(
        {"platform": platform, "handle": handle},
        {"$set": {"name": name, "data": data}},
        upsert=True
    )

def get_program(platform, handle):
    doc = programs.find_one({"platform": platform, "handle": handle})
    return doc['data'] if doc else None

def get_all_handles(platform):
    return [doc['handle'] for doc in programs.find({"platform": platform})]

def delete_program(platform, handle):
    programs.delete_one({"platform": platform, "handle": handle})