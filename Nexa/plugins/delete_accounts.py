import os
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from telethon import TelegramClient
from telethon.errors import AuthKeyUnregisteredError

from Nexa.bot import bot
from config import SESSION_DIR, API_ID, API_HASH
from Nexa.database.users import users_db


# ----------------------------
# Helpers
# ----------------------------

def normalize_phone(phone: str):
    return str(phone).replace("+", "").replace(".session", "").strip()


def get_base_session_path(user_id: int, session_name: str):
    session_name = normalize_phone(session_name)
    return os.path.join(
        SESSION_DIR,
        f"{user_id}_{session_name}"
    )


def get_session_file(user_id: int, session_name: str):
    return get_base_session_path(user_id, session_name) + ".session"


# ----------------------------
# Status Checker (UPDATED)
# ----------------------------

async def check_status(user_id: int, session_name: str):

    user = await users_db.find_one({"_id": user_id})
    status_map = user.get("account_status", {}) if user else {}

    # If already marked inactive in DB
    if status_map.get(session_name) == "inactive":
        return "Inactive", "❌"

    base_path = get_base_session_path(user_id, session_name)
    session_file = base_path + ".session"

    if not os.path.exists(session_file):
        return "Inactive", "❌"

    try:
        client = TelegramClient(base_path, API_ID, API_HASH)
        await client.connect()

        if not await client.is_user_authorized():
            await client.disconnect()

            # 🔥 Mark inactive in DB
            await users_db.update_one(
                {"_id": user_id},
                {"$set": {f"account_status.{session_name}": "inactive"}}
            )

            return "Inactive", "❌"

        await client.disconnect()

        # 🔥 Mark active in DB
        await users_db.update_one(
            {"_id": user_id},
            {"$set": {f"account_status.{session_name}": "active"}}
        )

        return "Active", "✅"

    except AuthKeyUnregisteredError:
        await users_db.update_one(
            {"_id": user_id},
            {"$set": {f"account_status.{session_name}": "inactive"}}
        )
        return "Inactive", "❌"

    except Exception:
        return "Inactive", "❌"


# ----------------------------
# Delete Menu
# ----------------------------

@bot.on_callback_query(filters.regex("^delete_accounts$"))
async def delete_accounts_menu(client, query):
    await query.answer()
    user_id = query.from_user.id

    user = await users_db.find_one({"_id": user_id})
    accounts = user.get("accounts", []) if user else []

    if not accounts:
        text = (
            "╰_╯ <b>NO ACCOUNTS TO DELETE</b>\n\n"
            "Add an account to start Advertising!"
        )
        buttons = [[
            InlineKeyboardButton("Add Account", callback_data="host_account"),
            InlineKeyboardButton("Back", callback_data="dashboard")
        ]]
        return await safe_edit(query, text, buttons)

    text = "╰_╯ <b>DELETE ACCOUNTS</b>\n\n"
    buttons = []

    for idx, session_name in enumerate(accounts, start=1):
        phone = f"+{normalize_phone(session_name)}"
        status, emoji = await check_status(user_id, session_name)

        text += f"{idx}. {phone} - {status} {emoji}\n"

        buttons.append([
            InlineKeyboardButton(f"{phone} ({status} {emoji})", callback_data="ignore"),
            InlineKeyboardButton("Delete", callback_data=f"delete_{session_name}")
        ])

    text += "\nChoose an account to delete:"

    buttons.append([
        InlineKeyboardButton("Back", callback_data="view_accounts")
    ])

    await safe_edit(query, text, buttons)


# ----------------------------
# Delete Account
# ----------------------------

@bot.on_callback_query(filters.regex(r"^delete_(.+)$"))
async def delete_account(client, query):
    await query.answer()
    user_id = query.from_user.id
    session_name = query.data.split("_", 1)[1]

    session_file = get_session_file(user_id, session_name)

    if os.path.exists(session_file):
        os.remove(session_file)

    await users_db.update_one(
        {"_id": user_id},
        {
            "$pull": {"accounts": session_name},
            "$unset": {f"account_status.{session_name}": ""}
        }
    )

    text = "<b>Account deleted!</b>\n\nAccount removed successfully. ✅"

    buttons = [[
        InlineKeyboardButton("Back", callback_data="view_accounts")
    ]]

    await safe_edit(query, text, buttons)


# ----------------------------
# Safe Edit
# ----------------------------

async def safe_edit(query, text, buttons):
    try:
        if query.message.photo:
            await query.message.edit_caption(
                caption=text,
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            await query.message.edit_text(
                text,
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    except:
        await query.message.reply_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(buttons)
    )
        
