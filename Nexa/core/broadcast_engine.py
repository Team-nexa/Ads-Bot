import os
import asyncio
import random
import traceback
from typing import Dict, List

from telethon import TelegramClient, functions
from telethon.errors import FloodWaitError, PeerFloodError, ChatWriteForbiddenError, AuthKeyUnregisteredError

from config import API_ID, API_HASH, SESSION_DIR
from Nexa.database.users import users_db
from Nexa.core.session_manager import list_user_sessions
from Nexa.core.logger import logger
from Nexa.core.broadcast_logs import send_log
from Nexa.core.profile_config import CUSTOM_LAST_NAME, CUSTOM_BIO

running_tasks: Dict[int, asyncio.Task] = {}
running_delays: Dict[int, int] = {}
clients: Dict[str, TelegramClient] = {}


def set_user_delay(user_id: int, delay: int):
    running_delays[user_id] = delay


async def start_broadcast(user_id: int) -> bool:
    if user_id in running_tasks and not running_tasks[user_id].done():
        return True

    user = await users_db.find_one({"_id": user_id})
    if not user or not user.get("advertising") or not user.get("ad_message"):
        return False

    sessions = list_user_sessions(user_id)
    if not sessions:
        return False

    for session_name in sessions:
        await update_profile_for_session(user_id, session_name)

    running_delays[user_id] = int(user.get("delay", 300))
    task = asyncio.create_task(broadcast_loop(user_id))
    running_tasks[user_id] = task

    await send_log(user_id, "🚀 <b>Broadcast started!</b> Logs will appear below:")
    return True


async def stop_broadcast(user_id: int):
    await users_db.update_one({"_id": user_id}, {"$set": {"advertising": False}})

    task = running_tasks.pop(user_id, None)
    if task and not task.done():
        task.cancel()

    running_delays.pop(user_id, None)

    for session_name in list_user_sessions(user_id):
        key = f"{user_id}_{session_name}"
        client = clients.get(key)
        if client:
            await client.disconnect()
            clients.pop(key, None)

    await send_log(user_id, "🛑 <b>Broadcast manually stopped</b>")


async def update_profile_for_session(user_id: int, session_name: str):
    session_file = os.path.join(SESSION_DIR, f"{session_name}.session")
    session_base = session_file.replace(".session", "")

    if not os.path.exists(session_file):
        return

    client = TelegramClient(session_base, API_ID, API_HASH)
    phone = session_name.split("_")[-1]
    if not phone.startswith("+"):
        phone = "+" + phone

    try:
        await client.connect()
        if not await client.is_user_authorized():
            await client.disconnect()
            return

        await client(functions.account.UpdateProfileRequest(
            last_name=CUSTOM_LAST_NAME,
            about=CUSTOM_BIO
        ))

        await send_log(user_id, f"📝 <b>Profile updated successfully for:</b> {phone}")

    except Exception as e:
        await send_log(user_id, f"⚠️ <b>Profile update failed for {phone}</b>: {str(e)}")
    finally:
        await client.disconnect()


async def broadcast_loop(user_id: int):
    try:
        while True:
            user = await users_db.find_one({"_id": user_id})
            if not user or not user.get("advertising"):
                break

            message = (user.get("ad_message") or "").strip()
            if not message:
                await asyncio.sleep(10)
                continue

            sessions = list_user_sessions(user_id)
            if not sessions:
                await asyncio.sleep(10)
                continue

            tasks = [send_from_session(user_id, s, message) for s in sessions]
            await asyncio.gather(*tasks)

            delay = running_delays.get(user_id, int(user.get("delay", 300)))
            await asyncio.sleep(delay)

    except asyncio.CancelledError:
        pass
    except Exception:
        logger.error(traceback.format_exc())
    finally:
        running_tasks.pop(user_id, None)
        running_delays.pop(user_id, None)
        await send_log(user_id, "🛑 <b>Broadcast stopped</b>")


async def send_from_session(user_id: int, session_name: str, message: str, target_ids: List[int] = None):
    session_file = os.path.join(SESSION_DIR, f"{session_name}.session")
    session_base = session_file.replace(".session", "")

    if not os.path.exists(session_file):
        return

    key = f"{user_id}_{session_name}"
    if key not in clients:
        clients[key] = TelegramClient(session_base, API_ID, API_HASH)
        await clients[key].connect()

    client = clients[key]
    success = 0
    failed = 0

    phone = session_name.split("_")[-1]
    if not phone.startswith("+"):
        phone = "+" + phone

    try:
        if not await client.is_user_authorized():
            await client.disconnect()
            clients.pop(key, None)
            return

        if target_ids:
            chats = []
            for chat_id in target_ids:
                try:
                    entity = await client.get_entity(chat_id)
                    chats.append(entity)
                except Exception:
                    continue
        else:
            chats = [d.entity for d in await client.get_dialogs(limit=None) if d.is_group or d.is_channel]

        for chat in chats:
            try:
                await client.send_message(chat, message)
                success += 1
                await users_db.update_one({"_id": user_id}, {"$inc": {"messages_sent": 1}})

                chat_name = getattr(chat, "title", str(chat))
                raw_chat_id = getattr(chat, "id", None)

                # 🔥 FIX: Proper Telegram supergroup/channel ID format
                if raw_chat_id:
                    if getattr(chat, "megagroup", False) or getattr(chat, "broadcast", False):
                        chat_id = f"-100{raw_chat_id}"
                    else:
                        chat_id = raw_chat_id
                else:
                    chat_id = "Unknown"

                await send_log(
                    user_id,
                    f"✅ <b>Sent to:</b> {chat_name} (<b>{chat_id}</b>) using {phone}"
                )

                await asyncio.sleep(random.randint(3, 5))

            except FloodWaitError as e:
                failed += 1
                await users_db.update_one({"_id": user_id}, {"$inc": {"messages_failed": 1}})
                await send_log(user_id, f"⏳ <b>FloodWait {e.seconds}s</b> using {phone}")
                await asyncio.sleep(e.seconds)

            except (PeerFloodError, ChatWriteForbiddenError):
                failed += 1
                await users_db.update_one({"_id": user_id}, {"$inc": {"messages_failed": 1}})
                await send_log(user_id, f"❌ <b>Cannot send to this chat with {phone}, skipping.</b>")
                continue

            except Exception:
                failed += 1
                await users_db.update_one({"_id": user_id}, {"$inc": {"messages_failed": 1}})
                continue

        await send_log(
            user_id,
            f"🕸 <u>Broadcast Round Completed</u>\n"
            f"✅ <b>𝘚𝘶𝘤𝘤𝘦𝘴:</b> {success}\n"
            f"❌ <b>𝘍𝘢𝘪𝘭𝘦𝘥:</b> {failed}\n"
            f"👤 <b>𝘈𝘤𝘤𝘰𝘶𝘯𝘵:</b> {phone}"
        )

    except Exception:
        logger.error(traceback.format_exc())
    finally:
        await client.disconnect()
