from Nexa.bot import bot
from pyrogram import filters

@bot.on_message(filters.command("test"))
async def test_command(client, message):
    await message.reply_text("✅ Plugin is working!")