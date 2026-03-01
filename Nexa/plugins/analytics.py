from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Nexa.bot import bot
from Nexa.database.users import users_db


def generate_progress_bar(percent: int) -> str:
    percent = max(0, min(percent, 100))
    filled_blocks = percent // 10
    return "░" * filled_blocks + "▓" * (10 - filled_blocks)


@bot.on_callback_query(filters.regex("^analytics$"))
async def analytics_menu_callback(client, query):
    await query.answer()

    user_id = query.from_user.id
    user = await users_db.find_one({"_id": user_id})

    if not user:
        await query.answer("No analytics data found.", show_alert=True)
        return

    broadcasts = int(user.get("broadcast_completed", 0))
    sent = int(user.get("messages_sent", 0))
    failed = int(user.get("messages_failed", 0))
    logger_fail = int(user.get("logger_failures", 0))
    accounts = user.get("accounts", [])
    delay = int(user.get("delay", 300))

    total_messages = sent + failed
    success_rate = int((sent / total_messages) * 100) if total_messages > 0 else 0
    progress_bar = generate_progress_bar(success_rate)
    active_accounts = len(accounts)

    text = (
        "<b>╰_╯ Nexa Analytics</b>\n\n"
        f"<u>Broadcast Cycles Completed:</u> <b>{broadcasts}</b>\n"
        f"<b>Total Messages Sent:</b> {sent}\n"
        f"<b>Total Failed Sends:</b> {failed}\n"
        f"<b>Logger Failures:</b> {logger_fail}\n"
        f"<b>Total Accounts:</b> {active_accounts}\n"
        f"<u>Delay:</u> <code>{delay}s</code>\n\n"
        f"<b>Success Rate:</b>\n{progress_bar} {success_rate}%"
    )

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Detailed Report", callback_data="detailed_report")],
            [InlineKeyboardButton("Back", callback_data="dashboard")]
        ]
    )

    try:
        await query.message.edit_text(
            text=text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        print("Analytics Edit Error:", e)