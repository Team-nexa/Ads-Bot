from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI, DB_NAME

client = AsyncIOMotorClient(MONGO_URI)

# Select database from .env
db = client[DB_NAME]


async def ensure_indexes():
    
    try:
        indexes = await db.users.index_information()
        if "user_id_1" in indexes:
            await db.users.drop_index("user_id_1")
            print("✅ Removed old 'user_id_1' index")
    except Exception as e:
        print(f"[DB WARNING] Index cleanup skipped: {e}")


async def check_connection() -> bool:
    try:
        await client.admin.command("ping")
        print("✅ MongoDB Connected Successfully")
        return True
    except Exception as e:
        print(f"[DB ERROR] Connection failed: {type(e).__name__}: {e}")
        return False