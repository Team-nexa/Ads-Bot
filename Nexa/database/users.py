from .mongo import db
from datetime import datetime
from pymongo.errors import DuplicateKeyError

users_db = db["users"]

# -------------------------------
# Helper: Validate user_id
# -------------------------------
def valid_user_id(user_id):
    return isinstance(user_id, int) and user_id > 0


# -------------------------------
# Get user by ID
# -------------------------------
async def get_user(user_id: int):
    if not valid_user_id(user_id):
        return None
    try:
        return await users_db.find_one({"_id": user_id})
    except Exception as e:
        print(f"[DB ERROR] get_user ({type(e).__name__}): {e}")
        return None


# -------------------------------
# Create or get user safely
# -------------------------------
async def get_or_create_user(user_id: int):
    if not valid_user_id(user_id):
        print("[DB WARNING] Invalid user_id")
        return None

    try:
        await users_db.update_one(
            {"_id": user_id},
            {
                "$setOnInsert": {
                    "accounts": [],
                    "max_accounts": 5,
                    "ad_message": None,
                    "delay": 300,
                    "advertising": False,
                    "created_at": datetime.utcnow()
                }
            },
            upsert=True
        )

    except DuplicateKeyError:
        # If old bad index still exists, ignore and continue
        pass

    except Exception as e:
        print(f"[DB ERROR] get_or_create_user ({type(e).__name__}): {e}")
        return None

    return await get_user(user_id)


# -------------------------------
# Accounts management
# -------------------------------
async def add_account(user_id: int, session_name: str):
    if not valid_user_id(user_id) or not session_name:
        return
    try:
        await users_db.update_one(
            {"_id": user_id},
            {"$addToSet": {"accounts": session_name}}
        )
    except Exception as e:
        print(f"[DB ERROR] add_account ({type(e).__name__}): {e}")


async def remove_account(user_id: int, session_name: str):
    if not valid_user_id(user_id) or not session_name:
        return
    try:
        await users_db.update_one(
            {"_id": user_id},
            {"$pull": {"accounts": session_name}}
        )
    except Exception as e:
        print(f"[DB ERROR] remove_account ({type(e).__name__}): {e}")


async def get_accounts(user_id: int):
    user = await get_user(user_id)
    if user:
        return user.get("accounts", [])
    return []


# -------------------------------
# Advertising settings
# -------------------------------
async def set_broadcast_status(user_id: int, status: bool):
    if not valid_user_id(user_id):
        return
    try:
        await users_db.update_one(
            {"_id": user_id},
            {"$set": {"advertising": bool(status)}}
        )
    except Exception as e:
        print(f"[DB ERROR] set_broadcast_status ({type(e).__name__}): {e}")


async def set_ad_message(user_id: int, message: str):
    if not valid_user_id(user_id):
        return
    try:
        await users_db.update_one(
            {"_id": user_id},
            {"$set": {"ad_message": message}}
        )
    except Exception as e:
        print(f"[DB ERROR] set_ad_message ({type(e).__name__}): {e}")


async def get_ad_message(user_id: int):
    user = await get_user(user_id)
    if user:
        return user.get("ad_message")
    return None


async def set_delay(user_id: int, delay: int):
    if not valid_user_id(user_id) or not isinstance(delay, int) or delay < 0:
        return
    try:
        await users_db.update_one(
            {"_id": user_id},
            {"$set": {"delay": delay}}
        )
    except Exception as e:
        print(f"[DB ERROR] set_delay ({type(e).__name__}): {e}")


# -------------------------------
# Delete user safely
# -------------------------------
async def delete_user(user_id: int):
    if not valid_user_id(user_id):
        return
    try:
        await users_db.delete_one({"_id": user_id})
    except Exception as e:
        print(f"[DB ERROR] delete_user ({type(e).__name__}): {e}")