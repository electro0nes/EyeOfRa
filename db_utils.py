from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()

MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASS = os.getenv("MONGO_PASS")
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_DB   = os.getenv("MONGO_DB", "bugbounty")

if MONGO_USER and MONGO_PASS:
    MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}"
else:
    MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}"

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
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