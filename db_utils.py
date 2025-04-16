from mongoengine import connect, Document, StringField, DictField
import os
from dotenv import load_dotenv
load_dotenv()

MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASS = os.getenv("MONGO_PASS")
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_DB   = os.getenv("MONGO_DB", "bugbounty")

# Connect using mongoengine
connect(
    db=MONGO_DB,
    host=MONGO_HOST,
    port=MONGO_PORT,
    username=MONGO_USER,
    password=MONGO_PASS,
)

class Program(Document):
    platform = StringField(required=True)
    handle = StringField(required=True)
    name = StringField()
    data = DictField()

    meta = {
        'collection': 'programs',
        'indexes': [
            {'fields': ('platform', 'handle'), 'unique': True}
        ]
    }

# Functions using mongoengine ORM
def insert_or_update_program(platform, handle, name, data):
    Program.objects(platform=platform, handle=handle).update_one(
        set__name=name,
        set__data=data,
        upsert=True
    )

def get_program(platform, handle):
    prog = Program.objects(platform=platform, handle=handle).first()
    return prog.data if prog else None

def get_all_handles(platform):
    return [p.handle for p in Program.objects(platform=platform)]

def delete_program(platform, handle):
    Program.objects(platform=platform, handle=handle).delete()