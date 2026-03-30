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
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from Nexa.bot import bot
from Nexa.database.users import users_db
from Nexa.core.broadcast_engine import set_user_delay

waiting_delay = set()

def get_mode(delay: int) -> str:
    if delay <= 300:
        return "Aggressive 🔴"
    elif delay <= 600:
        return "Safe & Balanced 🟡"
    return "Conservative 🟢"

@bot.on_callback_query(filters.regex("^set_delay$"))
async def set_delay_ui(client, query):
    await query.answer()
    user_id = query.from_user.id
    user = await users_db.find_one({"_id": user_id})
    current_delay = user.get("delay", 300) if user else 300

    text = (
        "╰_╯ <b>SET BROADCAST CYCLE INTERVAL</b>\n\n"
        f"Current Interval: <b>{current_delay} seconds</b>\n\n"
        "Recommended Intervals:\n"
        "• 300s - Aggressive (5 min) 🔴\n"
        "• 600s - Safe & Balanced (10 min) 🟡\n"
        "• 1200s - Conservative (20 min) 🟢\n\n"
        "To set a custom time interval, send a number (in seconds):\n"
        "(Note: Very short intervals can put your accounts at risk.)"
    )

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("20min 🟢", callback_data="delay_1200"),
            InlineKeyboardButton("5min 🔴", callback_data="delay_300"),
            InlineKeyboardButton("10min 🟡", callback_data="delay_600"),
        ],
        [InlineKeyboardButton("🔙 Back", callback_data="dashboard")]
    ])

    waiting_delay.add(user_id)
    await query.message.edit_text(text, reply_markup=buttons, parse_mode=ParseMode.HTML)

@bot.on_callback_query(filters.regex("^delay_(\\d+)$"))
async def preset_delay(client, query):
    await query.answer()
    user_id = query.from_user.id
    delay = int(query.data.split("_")[1])

    await users_db.update_one({"_id": user_id}, {"$set": {"delay": delay}}, upsert=True)
    set_user_delay(user_id, delay)
    waiting_delay.discard(user_id)
    mode = get_mode(delay)

    updated_text = (
        "╰_╯ <b>CYCLE INTERVAL UPDATED!</b>\n\n"
        f"New Interval: <b>{delay} seconds</b>\n"
        f"Mode: <b>{mode}</b>\n\n"
        "Ready for broadcasting!"
    )

    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="set_delay")]])
    await query.message.edit_text(updated_text, reply_markup=buttons, parse_mode=ParseMode.HTML)

@bot.on_message(filters.private & filters.text & ~filters.command(["start"]), group=2)
async def custom_delay(client, message):
    user_id = message.from_user.id
    if user_id not in waiting_delay:
        return
    if not message.text.isdigit():
        await message.reply("⚠ Send a valid number in seconds.")
        return

    delay = int(message.text)
    if delay < 60:
        await message.reply("⚠ Minimum 60 seconds allowed.")
        return

    await users_db.update_one({"_id": user_id}, {"$set": {"delay": delay}}, upsert=True)
    set_user_delay(user_id, delay)
    waiting_delay.discard(user_id)
    mode = get_mode(delay)

    updated_text = (
        "╰_╯ <b>CYCLE INTERVAL UPDATED!</b>\n\n"
        f"New Interval: <b>{delay} seconds</b>\n"
        f"Mode: <b>{mode}</b>\n\n"
        "Ready for broadcasting!"
    )

    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="set_delay")]])
    await message.reply(updated_text, reply_markup=buttons, parse_mode=ParseMode.HTML)
# ── Powered by Nexa Coders ──
