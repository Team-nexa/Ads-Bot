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
import os
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from telethon import TelegramClient
from telethon.errors import AuthKeyUnregisteredError

from Nexa.bot import bot
from config import API_ID, API_HASH, SESSION_DIR
from Nexa.database.users import users_db

os.makedirs(SESSION_DIR, exist_ok=True)


def clean_phone(phone: str):
    phone = str(phone).replace("+", "").strip()
    return f"+{phone}"


async def check_status(user_id: int, session_name: str):

    user = await users_db.find_one({"_id": user_id})
    status_map = user.get("account_status", {}) if user else {}

    if status_map.get(session_name) == "inactive":
        return "Inactive", "❌"

    session_path = os.path.join(
        SESSION_DIR, f"{session_name}.session"
    )

    if not os.path.isfile(session_path):
        return "Inactive", "❌"

    try:
        client = TelegramClient(session_path.replace(".session", ""), API_ID, API_HASH)
        await client.connect()

        if not await client.is_user_authorized():
            await client.disconnect()

            await users_db.update_one(
                {"_id": user_id},
                {"$set": {f"account_status.{session_name}": "inactive"}}
            )

            return "Inactive", "❌"

        await client.disconnect()

        await users_db.update_one(
            {"_id": user_id},
            {"$set": {f"account_status.{session_name}": "active"}}
        )

        return "Active", "✅"

    except AuthKeyUnregisteredError:
        return "Inactive", "❌"
    except Exception:
        return "Inactive", "❌"


@bot.on_callback_query(filters.regex("^view_accounts$"))
async def view_accounts(client, query):
    await query.answer()
    user_id = query.from_user.id

    user = await users_db.find_one({"_id": user_id})
    accounts = user.get("accounts", []) if user else []

    if not accounts:
        text = "╰_╯ NO ACCOUNTS TO DELETE\n\nAdd an account to start Advertising!"

        buttons = [[
            InlineKeyboardButton("Add Account", callback_data="host_account"),
            InlineKeyboardButton("Back", callback_data="dashboard")
        ]]

        return await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    text = "╰_╯ HOSTED ACCOUNTS\n\n"
    buttons = []

    for idx, session_name in enumerate(accounts, start=1):
        status, emoji = await check_status(user_id, session_name)
        phone = clean_phone(session_name)

        text += f"{idx}. {phone} - {status} {emoji}\n"

        buttons.append([
            InlineKeyboardButton(
                f"{phone} ({status} {emoji})",
                callback_data="ignore"
            ),
            InlineKeyboardButton(
                "Delete",
                callback_data=f"confirmdelete_{session_name}"
            )
        ])

    text += "\n╰_╯ Choose an action:"

    buttons.append([InlineKeyboardButton("Add Account", callback_data="host_account")])
    buttons.append([InlineKeyboardButton("Back", callback_data="dashboard")])

    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons)
        )
    

# ── Powered by Nexa Coders ──
