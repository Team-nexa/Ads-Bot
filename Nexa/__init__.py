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
from .database.mongo import db
from .database import users


from .core import broadcast_engine
from .core import session_manager
from .core import task_manager


# Do NOT import plugins here


# ── Powered by Nexa Coders ──
