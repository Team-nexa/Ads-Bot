from telegram import Bot
from config import LOGGER_BOT_TOKEN
from Nexa.core.logger import logger

logger_bot = Bot(token=LOGGER_BOT_TOKEN)

async def send_log(user_id: int, text: str):
    try:
        await logger_bot.send_message(
            chat_id=user_id,
            text=text,
            disable_web_page_preview=True,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Failed to send log to {user_id}: {e}")