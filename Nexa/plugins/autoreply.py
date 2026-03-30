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
from Nexa.bot import bot

AUTO_REPLY_TEXT = (
    "**╰_╯ AUTO REPLY FEATURE**\n\n"
    "This feature is coming soon!\n"
    "Stay tuned for automated reply capabilities to enhance your campaigns.\n"
    "This feature is Not Available Right Now"
)

@bot.on_callback_query(filters.regex("^auto_reply$"))
async def auto_reply_callback(client, query):
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Back", callback_data="dashboard")]]
    )
    await query.message.edit_text(
        AUTO_REPLY_TEXT,
        reply_markup=keyboard
    )
# ── Powered by Nexa Coders ──
