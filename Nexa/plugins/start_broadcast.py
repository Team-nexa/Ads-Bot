from pyrogram import filters
from Nexa.bot import bot
from Nexa.database.users import users_db
from Nexa.core.broadcast_engine import start_broadcast


@bot.on_callback_query(filters.regex("^start_broadcast$"))
async def start_broadcast_callback(client, query):
    user_id = query.from_user.id
    user = await users_db.find_one({"_id": user_id})

    if not user:
        await query.answer("User not found ❌", show_alert=True)
        return

    if not user.get("accounts"):
        await query.answer("No accounts hosted ❌", show_alert=True)
        return

    if not user.get("ad_message"):
        await query.answer("Set ad message first ❌", show_alert=True)
        return

    if user.get("advertising"):
        await query.answer("Broadcast already running 🚀", show_alert=True)
        return

    # Enable advertising
    await users_db.update_one(
        {"_id": user_id},
        {"$set": {"advertising": True}}
    )

    # 🔥 Start broadcast (profile update happens inside broadcast_engine)
    started = await start_broadcast(user_id)

    if not started:
        await query.answer("Failed to start broadcast ❌", show_alert=True)
        return

    await query.answer("🚀 Broadcast Started")

    await query.message.edit_text(
        "╰_╯ BROADCAST STARTED\n\n"
        "Ads are being sent to all your groups/channels.\n"
        "Use Stop Ads ⏸️ to stop broadcasting."
    )
