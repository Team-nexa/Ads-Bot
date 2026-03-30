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
from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from Nexa.bot import bot
from Nexa.database.users import set_ad_message, get_ad_message
from config import LOGGER_BOT_TOKEN

waiting_for_ad = set()

logger_bot = Client("logger_bot", bot_token=LOGGER_BOT_TOKEN)


@bot.on_callback_query(filters.regex("^set_msg$"))
async def set_message_ui(client, query):
    await query.answer()
    user_id = query.from_user.id
    current_msg = await get_ad_message(user_id)

    text = "╰_╯ **SET YOUR AD MESSAGE**\n\n"
    text += "**Current Ad Message:**\n\n"
    if current_msg:
        text += f"`{current_msg}`\n\n"
    else:
        text += "_No message set yet._\n\n"

    text += (
        "**Tips for effective ads:**\n"
        "• Keep it concise and engaging\n"
        "• Use emojis for flair\n"
        "• Include clear call-to-action\n"
        "• Avoid excessive caps or spam words\n\n"
        "**Send your ad message now:**"
    )

    buttons = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔙 Back", callback_data="dashboard")]]
    )

    waiting_for_ad.add(user_id)

    await query.message.edit_text(
        text=text,
        reply_markup=buttons,
        parse_mode=ParseMode.MARKDOWN
    )


@bot.on_message(
    filters.private & filters.text & ~filters.command(["start"]),
    group=1
)
async def receive_ad_message(client, message):
    user_id = message.from_user.id
    if user_id not in waiting_for_ad:
        return

    ad_text = message.text.strip()
    if not ad_text:
        await message.reply(
            "⚠ Ad message cannot be empty.",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    if len(ad_text) > 4096:
        await message.reply(
            "⚠ Message too long. Keep under 4096 characters.",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    await set_ad_message(user_id, ad_text)
    waiting_for_ad.discard(user_id)

    await message.reply(
        "╰_╯ **AD MESSAGE SET!** ✅\n\n"
        f"**Message Preview:**\n`{ad_text}`\n\n"
        "Ready to broadcast!\n"
        "Start your campaign from the dashboard.",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Dashboard 🚪", callback_data="dashboard")]]
        ),
        parse_mode=ParseMode.MARKDOWN
    )

    try:
        chat = await bot.get_chat(user_id)
        if chat.type in ["private"]:
            await logger_bot.send_message(
                chat_id="me",
                text=f"📝 Ad message updated by user {user_id}:\n\n`{ad_text}`",
                parse_mode=ParseMode.MARKDOWN
            )
    except:
        pass
# ── Powered by Nexa Coders ──
