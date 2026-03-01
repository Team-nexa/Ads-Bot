from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import MessageNotModified, RPCError

from Nexa.bot import bot
from config import START_IMAGE, START_TEXT, DASHBOARD_TEXT
from Nexa.database.users import get_or_create_user, get_accounts, get_ad_message


# ==========================
# REUSABLE START MENU
# ==========================

async def send_start_menu(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Dashboard", callback_data="dashboard")],
        [
            InlineKeyboardButton("Updates", url="https://t.me/NexaCoders"),
            InlineKeyboardButton("Support", url="https://t.me/NexaCoders")
        ],
        [InlineKeyboardButton("How To Use", url="https://t.me/LustStreet")],
        [InlineKeyboardButton("Powered By", url="https://t.me/NexaCoders")]
    ])

    try:
        await message.reply_photo(
            photo=START_IMAGE,
            caption=START_TEXT,
            reply_markup=keyboard
        )
    except Exception:
        await message.reply_text(
            text=START_TEXT,
            reply_markup=keyboard
        )


# ==========================
# /start COMMAND
# ==========================

@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    await send_start_menu(client, message)


# ==========================
# DASHBOARD CALLBACK
# ==========================

@bot.on_callback_query(filters.regex("^dashboard$"))
async def dashboard_callback(client, query: CallbackQuery):
    await query.answer()

    user_id = query.from_user.id
    if not isinstance(user_id, int) or user_id <= 0:
        return await query.answer("❌ Invalid user ID.", show_alert=True)

    user = await get_or_create_user(user_id)
    if not user:
        return await query.answer("❌ Could not fetch user data.", show_alert=True)

    accounts = await get_accounts(user_id) or []
    ad_message = await get_ad_message(user_id)

    account_count = len(accounts)
    max_accounts = user.get("max_accounts", 5)
    ad_status = "Set ✅" if ad_message else "Not Set ⭕"
    delay = user.get("delay", 300)
    running_status = "Running 🚀" if user.get("advertising", False) else "Paused ⏸️"

    formatted_dashboard = DASHBOARD_TEXT.format(
        account_count=account_count,
        max_accounts=max_accounts,
        ad_status=ad_status,
        delay=delay,
        running_status=running_status
    )

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Add Accounts", callback_data="host_account"),
            InlineKeyboardButton("My Accounts", callback_data="view_accounts")
        ],
        [
            InlineKeyboardButton("Set Ad Message", callback_data="set_msg"),
            InlineKeyboardButton("Set Time Interval", callback_data="set_delay")
        ],
        [
            InlineKeyboardButton("Start Ads ▶️", callback_data="start_broadcast"),
            InlineKeyboardButton("Stop Ads ⏸️", callback_data="stop_broadcast")
        ],
        [
            InlineKeyboardButton("Delete Accounts", callback_data="delete_accounts"),
            InlineKeyboardButton("Analytics", callback_data="analytics")
        ],
        [
            InlineKeyboardButton("Auto Reply", callback_data="auto_reply"),
            InlineKeyboardButton("Back", callback_data="back")
        ]
    ])

    try:
        if query.message.photo:
            await query.message.edit_caption(
                caption=formatted_dashboard,
                reply_markup=buttons
            )
        else:
            await query.message.edit_text(
                text=formatted_dashboard,
                reply_markup=buttons
            )
    except (MessageNotModified, RPCError):
        pass


# ==========================
# BACK BUTTON
# ==========================

@bot.on_callback_query(filters.regex("^back$"))
async def back_callback(client, query: CallbackQuery):
    await query.answer()
    await send_start_menu(client, query.message)
