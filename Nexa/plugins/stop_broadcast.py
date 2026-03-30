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
from pyrogram import filters
from Nexa.bot import bot
from Nexa.database.users import users_db
from Nexa.core.broadcast_engine import stop_broadcast


@bot.on_callback_query(filters.regex("^stop_broadcast$"))
async def stop_broadcast_callback(client, query):
    user_id = query.from_user.id
    user = await users_db.find_one({"_id": user_id})

    if not user:
        await query.answer("User not found ❌", show_alert=True)
        return

    if not user.get("advertising"):
        await query.answer("Broadcast not running ❌", show_alert=True)
        return

    await stop_broadcast(user_id)

    await query.answer("Broadcast Stopped 🛑", show_alert=True)
    await query.message.edit_text(
        "╰_╯ BROADCAST STOPPED\n\n"
        "Advertising has been successfully stopped."
    )
# ── Powered by Nexa Coders ──
