from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Nexa.bot import bot
from Nexa.database.users import users_db
from datetime import datetime

@bot.on_callback_query(filters.regex("^detailed_report$"))
async def detailed_report_callback(client, query):
    await query.answer()

    user_id = query.from_user.id
    user = await users_db.find_one({"_id": user_id})

    if not user:
        await query.answer("No detailed report available.", show_alert=True)
        return

    sent = int(user.get("messages_sent", 0))
    failed = int(user.get("messages_failed", 0))
    broadcasts = int(user.get("broadcast_completed", 0))
    logger_fail = int(user.get("logger_failures", 0))
    accounts = user.get("accounts", [])
    delay = int(user.get("delay", 300))

    total_accounts = len(accounts)
    active_accounts = total_accounts  
    inactive_accounts = 0

    today = datetime.now().strftime("%d/%m/%y")

    text = (
        "<b>╰_╯ DETAILED ANALYTICS REPORT:</b>\n\n"
        f"<u>Date:</u> {today}\n"
        f"<b>User ID:</b> <code>{user_id}</code>\n\n"
        "<b>Broadcast Stats:</b>\n"
        f"- <u>Total Sent:</u> {sent}\n"
        f"- <u>Total Failed:</u> {failed}\n"
        f"- <u>Total Broadcasts:</u> {broadcasts}\n\n"
        "<b>Logger Stats:</b>\n"
        f"- <u>Logger Failures:</u> {logger_fail}\n"
        "- Last Failure: <b>None</b>\n\n"
        "<b>Account Stats:</b>\n"
        f"- Total Accounts: <u>{total_accounts}</u>\n"
        f"- <b>Active Accounts:</b> {active_accounts} 🟢\n"
        f"- <u>Inactive Accounts:</u> {inactive_accounts} 🔴\n\n"
        f"<b>Current Delay:</b> <code>{delay}s</code>"
    )

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Back", callback_data="analytics")]]
    )

    try:
        await query.message.edit_text(
            text=text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        print("Detailed Report Edit Error:", e)