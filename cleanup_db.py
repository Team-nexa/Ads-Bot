#
# ── Nexa Coders ─────────────────────────────────────
# Telegram Ads Bot
#
# © 2026 NexaCoders. All Rights Reserved.
# Github  : https://github.com/Team-nexa
# Project : https://github.com/Team-nexa/Ads-Bot
#
# Licensed under the MIT License.
# ───────────────────────────────────────────────────
#
from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client["nexa"]

result1 = db.users.delete_many({"user_id": None})
result2 = db.users.delete_many({"user_id": {"$exists": False}})

print("Deleted user_id: null →", result1.deleted_count)
print("Deleted missing user_id →", result2.deleted_count)
# ── Powered by Nexa Coders ──
