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
import asyncio
import time

from pyrogram import filters
from pyrogram.errors import Forbidden, RPCError
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from Nexa.bot import bot as app
from config import API_ID, API_HASH, SESSION_DIR, LOGGER_BOT_TOKEN
from telegram import Bot
from Nexa.core.logger import logger

from telethon import TelegramClient
from telethon.errors import (
    SessionPasswordNeededError,
    PasswordHashInvalidError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    FloodWaitError,
)

from Nexa.database.users import users_db

os.makedirs(SESSION_DIR, exist_ok=True)

user_states = {}
user_locks = {}
flood_waits = {}

logger_bot = Bot(token=LOGGER_BOT_TOKEN)

def get_lock(user_id: int) -> asyncio.Lock:
    if user_id not in user_locks:
        user_locks[user_id] = asyncio.Lock()
    return user_locks[user_id]

async def log_event(user_id: int, event_type: str, phone: str):
    if not LOGGER_BOT_TOKEN:
        return
    try:
        phone = str(phone)
        if event_type == "cleanup":
            text = f"⚠️ <b>Session cleanup:</b> <code>{phone}</code> session removed."
        elif event_type == "otp":
            text = f"<b>╰_╯ OTP requested for phone number:</b> <code>{phone}</code>"
        elif event_type == "success":
            text = f"<b>╰_╯ Account successfully logged in:</b> <code>{phone}</code>"
        elif event_type == "failed":
            text = f"❌ <b>Failed to send OTP for phone:</b> <code>{phone}</code>"
        else:
            text = f"<code>{phone}</code> - {event_type}"
        await logger_bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    except Forbidden:
        pass
    except RPCError as e:
        logger.error(f"[ACCOUNT LOG RPC ERROR] {e}")
    except Exception as e:
        logger.error(f"[ACCOUNT LOG ERROR] {e}")

def otp_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("1", callback_data="otp_1"),
            InlineKeyboardButton("2", callback_data="otp_2"),
            InlineKeyboardButton("3", callback_data="otp_3")
        ],
        [
            InlineKeyboardButton("4", callback_data="otp_4"),
            InlineKeyboardButton("5", callback_data="otp_5"),
            InlineKeyboardButton("6", callback_data="otp_6")
        ],
        [
            InlineKeyboardButton("7", callback_data="otp_7"),
            InlineKeyboardButton("8", callback_data="otp_8"),
            InlineKeyboardButton("9", callback_data="otp_9")
        ],
        [
            InlineKeyboardButton("⌫", callback_data="otp_del"),
            InlineKeyboardButton("0", callback_data="otp_0"),
            InlineKeyboardButton("❌", callback_data="otp_cancel")
        ],
        [
            InlineKeyboardButton("Show Code", url="tg://openmessage?user_id=777000")
        ]
    ])

def format_otp(otp: str) -> str:
    if not otp:
        return "_____"
    return "*" * len(otp)

def otp_text(phone: str, otp: str = "", extra: str = "") -> str:
    text = (
        f"╰_╯ OTP sent to {phone}! ✅\n\n"
        "Enter the OTP using the keypad below\n\n"
        f"Current : {format_otp(otp)}\n\n"
        "Format  : 12345 (no spaces needed)\n"
        "Valid for: 5 minutes"
    )
    if extra:
        text += f"\n\n{extra}"
    return text

async def otp_timeout(user_id: int, seconds: int = 300):
    try:
        await asyncio.sleep(seconds)
    except asyncio.CancelledError:
        return
    state = user_states.get(user_id)
    if not state:
        return
    if state.get("step") not in ["OTP", "2FA"]:
        return
    try:
        await safe_edit(
            state["chat_id"],
            state["process_msg_id"],
            "⏰ OTP expired (5 minutes timeout)\n\nProcess cancelled."
        )
    except:
        pass
    await cleanup(user_id)

async def safe_edit(chat_id, message_id, text, reply_markup=None):
    try:
        await app.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    except RPCError:
        pass

async def cleanup(user_id: int):
    state = user_states.get(user_id)
    if not state:
        return
    if state.get("timeout"):
        state["timeout"].cancel()
    if state.get("client") and state.get("step") != "SUCCESS":
        try:
            await state["client"].disconnect()
        except:
            pass
    if state.get("phone") and state.get("step") != "SUCCESS":
        await log_event(user_id, "cleanup", state.get("phone"))
    user_states.pop(user_id, None)
    user_locks.pop(user_id, None)
    if user_id in flood_waits:
        del flood_waits[user_id]

@app.on_callback_query(filters.regex("^host_account$"))
async def start_host(client, query):
    user_id = query.from_user.id
    await cleanup(user_id)
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Cancel", callback_data="dashboard")]])
    await safe_edit(
        query.message.chat.id,
        query.message.id,
        "<b>╰_╯ HOST NEW ACCOUNT</b>\n\nSecure Account Hosting\n\n"
        "Enter your phone number with country code:\n\n"
        "Example: <code>+1234567890</code>\nYour data is encrypted and secure.",
        reply_markup=keyboard
    )
    user_states[user_id] = {
        "step": "PHONE",
        "phone": None,
        "client": None,
        "otp": "",
        "timeout": None,
        "process_msg_id": None,
        "chat_id": query.message.chat.id
    }

@app.on_message(filters.private & filters.text)
async def handle_text(client, message):
    user_id = message.from_user.id
    if user_id not in user_states:
        return
    async with get_lock(user_id):
        state = user_states[user_id]
        await message.delete()

        if state["step"] == "PHONE":
            phone = message.text.strip()
            if not phone.startswith("+"):
                keyboard = InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Back", callback_data="back")]]
                )
                await app.send_message(
                    state["chat_id"],
                    "❌ <b>Invalid phone number!</b>\n\n"
                    "<u>Please use international format.</u>\n"
                    "Example: <code>+1234567890</code>",
                    parse_mode=ParseMode.HTML,
                    reply_markup=keyboard
                )
                return

            msg = await app.send_message(
                state["chat_id"],
                f"⏳ Hold! We're trying to OTP...\n\n"
                f"<u>Phone</u>: <code>{phone}</code>\n\n"
                "Please wait a moment.",
                parse_mode=ParseMode.HTML
            )
            state["process_msg_id"] = msg.id

            try:
                session_path = f"{SESSION_DIR}/{user_id}_{phone.replace('+','')}.session"
                client_ = TelegramClient(session_path, API_ID, API_HASH)
                await client_.connect()
                
                if user_id in flood_waits:
                    wait_time = flood_waits[user_id]
                    await safe_edit(
                        state["chat_id"],
                        state["process_msg_id"],
                        f"⏳ <b>Rate limited by Telegram!</b>\n\n"
                        f"Phone: <code>{phone}</code>\n\n"
                        f"Wait {wait_time//3600:02d}:{(wait_time%3600)//60:02d}:{wait_time%60:02d} "
                        f"before trying again.\n\n"
                        f"<u>Reason:</u> Too many OTP requests.",
                        parse_mode=ParseMode.HTML
                    )
                    await cleanup(user_id)
                    return

                sent_code = await client_.send_code_request(phone)
                flood_waits[user_id] = 0

                state.update({
                    "phone": phone,
                    "client": client_,
                    "step": "OTP",
                    "otp": "",
                    "phone_code_hash": sent_code.phone_code_hash
                })
                state["timeout"] = asyncio.create_task(otp_timeout(user_id))

                await safe_edit(
                    state["chat_id"],
                    state["process_msg_id"],
                    otp_text(phone),
                    reply_markup=otp_keyboard()
                )
                await log_event(user_id, "otp", phone)

            except FloodWaitError as e:
                wait_seconds = e.seconds
                flood_waits[user_id] = wait_seconds
                keyboard = InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Back", callback_data="back")]]
                )
                await safe_edit(
                    state["chat_id"],
                    state["process_msg_id"],
                    f"⏳ <b>Telegram Rate Limit!</b>\n\n"
                    f"Phone: <code>{phone}</code>\n\n"
                    f"Wait {wait_seconds//3600:02d}:{(wait_seconds%3600)//60:02d}:{wait_seconds%60:02d} "
                    f"before next attempt.\n\n"
                    f"<u>Reason:</u> FloodWaitError - Too many OTP requests from same IP/session.",
                    reply_markup=keyboard,
                    parse_mode=ParseMode.HTML
                )
                await log_event(user_id, "failed", phone)
                await cleanup(user_id)
            except Exception as e:
                keyboard = InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Back", callback_data="back")]]
                )
                error_msg = str(e)
                if "wait" in error_msg.lower() and "seconds" in error_msg.lower():
                    import re
                    wait_match = re.search(r'(\d+)', error_msg)
                    if wait_match:
                        wait_seconds = int(wait_match.group(1))
                        flood_waits[user_id] = wait_seconds
                        await safe_edit(
                            state["chat_id"],
                            state["process_msg_id"],
                            f"⏳ <b>Telegram Flood Limit!</b>\n\n"
                            f"Phone: <code>{phone}</code>\n\n"
                            f"Wait {wait_seconds//3600:02d}:{(wait_seconds%3600)//60:02d}:{wait_seconds%60:02d} "
                            f"before retry.\n\n"
                            f"<u>Reason:</u> Flood protection active.",
                            reply_markup=keyboard,
                            parse_mode=ParseMode.HTML
                        )
                    else:
                        await safe_edit(
                            state["chat_id"],
                            state["process_msg_id"],
                            "❌ <b>Failed to send OTP!</b>\n\n"
                            f"<u>Error:</u> {error_msg}\n\n"
                            "<b>Contact support:</b> @NexaMeetup",
                            reply_markup=keyboard,
                            parse_mode=ParseMode.HTML
                        )
                else:
                    await safe_edit(
                        state["chat_id"],
                        state["process_msg_id"],
                        "❌ <b>Failed to send OTP!</b>\n\n"
                        f"<u>Error:</u> {error_msg}\n\n"
                        "<b>Contact support:</b> @NexaMeetup",
                        reply_markup=keyboard,
                        parse_mode=ParseMode.HTML
                    )
                await log_event(user_id, "failed", phone)
                await cleanup(user_id)
        elif state["step"] == "2FA":
            try:
                await state["client"].sign_in(password=message.text.strip())
                state["step"] = "SUCCESS"
                await log_event(user_id, "success", state["phone"])
                await finalize_success(user_id)
            except PasswordHashInvalidError:
                await safe_edit(
                    state["chat_id"],
                    state["process_msg_id"],
                    otp_text(state["phone"], state["otp"], "🔐 Invalid 2FA password. Try again.")
                )

@app.on_callback_query(filters.regex("^otp_"))
async def otp_handler(client, query):
    user_id = query.from_user.id
    if user_id not in user_states:
        return await query.answer("Session expired", show_alert=True)
    async with get_lock(user_id):
        state = user_states[user_id]
        data = query.data
        if data == "otp_cancel":
            await safe_edit(state["chat_id"], state["process_msg_id"], "OTP entry cancelled.")
            await cleanup(user_id)
            return
        if data == "otp_del":
            state["otp"] = state["otp"][:-1]
        else:
            if len(state["otp"]) < 5:
                state["otp"] += data.split("_")[1]
        if len(state["otp"]) == 5:
            await safe_edit(
                state["chat_id"],
                state["process_msg_id"],
                otp_text(state["phone"], state["otp"], "Verifying OTP..."),
                reply_markup=otp_keyboard()
            )
            await asyncio.sleep(2)
            await verify_otp(user_id)
        else:
            await safe_edit(
                state["chat_id"],
                state["process_msg_id"],
                otp_text(state["phone"], state["otp"]),
                reply_markup=otp_keyboard()
            )

async def verify_otp(user_id: int):
    state = user_states[user_id]
    try:
        await state["client"].sign_in(
            phone=state["phone"],
            code=state["otp"],
            phone_code_hash=state["phone_code_hash"]
        )
        state["step"] = "SUCCESS"
        await log_event(user_id, "success", state["phone"])
        await finalize_success(user_id)
    except PhoneCodeInvalidError:
        state["otp"] = ""
        await safe_edit(
            state["chat_id"],
            state["process_msg_id"],
            otp_text(state["phone"], "", "❌ Invalid OTP. Try again."),
            reply_markup=otp_keyboard()
        )
    except PhoneCodeExpiredError:
        await safe_edit(
            state["chat_id"],
            state["process_msg_id"],
            "⏰ OTP expired.\n\nSend phone number again."
        )
        await cleanup(user_id)
    except SessionPasswordNeededError:
        state["step"] = "2FA"
        await safe_edit(
            state["chat_id"],
            state["process_msg_id"],
            otp_text(state["phone"], state["otp"], "🔐 2FA Detected! Enter your cloud password:"),
            reply_markup=None
        )

async def finalize_success(user_id: int):
    state = user_states[user_id]
    if state.get("timeout"):
        state["timeout"].cancel()
    phone = state["phone"]
    await users_db.update_one(
        {"_id": user_id},
        {"$push": {"accounts": phone}},
        upsert=True
    )
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Dashboard", callback_data="dashboard")]])
    await safe_edit(
        state["chat_id"],
        state["process_msg_id"],
        f"╰_╯ Account added! ✅\n\nPhone: {phone}\n• Account is ready for broadcasting!\n"
        "Note: Profile bio and name will be updated during first broadcast.",
        reply_markup=keyboard
    )
    user_states.pop(user_id, None)
    user_locks.pop(user_id, None)

@app.on_callback_query(filters.regex("^dashboard$"))
async def dashboard_cleanup(client, query):
    await cleanup(query.from_user.id)
    await query.answer("🏠 Dashboard")
# ── Powered by Nexa Coders ──
