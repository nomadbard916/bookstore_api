from databases import Database
from utils.const import DB_URL

db = Database(DB_URL)


async def connect_db():
    db = Database(DB_URL)
    await db.connect()
    return db


async def disconnect_db(db):
    await db.disconnect()
