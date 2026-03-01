import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
LOGGER_BOT_TOKEN = os.getenv("LOGGER_BOT_TOKEN", "")

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise ValueError("API_ID, API_HASH, and BOT_TOKEN must be set in environment variables.")

MONGO_URI = os.getenv("MONGO_URI", "")
DB_NAME = os.getenv("DB_NAME", "nexa_bot")

if not MONGO_URI:
    raise ValueError("MONGO_URI must be set in environment variables.")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_DIR = os.path.join(BASE_DIR, "Nexa", "sessions")
os.makedirs(SESSION_DIR, exist_ok=True)

MAX_ACCOUNTS = int(os.getenv("MAX_ACCOUNTS", 5))
DEFAULT_DELAY = int(os.getenv("DEFAULT_DELAY", 300))


HOST_SESSION = "host"


FORCE_JOIN_TEXT = """
**╰_╯ WELCOME TO FREE ADS BOT**

To unlock the full experience, please join our official channel and group first!

After joining, click Dashboard again 🚀
"""

START_IMAGE = os.getenv(
    "START_IMAGE",
    "https://files.catbox.moe/43767f.jpg"
)

START_TEXT = """╰_╯ Welcome to @NexaCoders **Free Ads Bot** — The Future of Telegram Automation
• Premium Ad Broadcasting  
• Smart Delays  
• Multi-Account Support  

"""

DASHBOARD_TEXT = """╰_╯ **Ads DASHBOARD**
• Hosted Accounts: `{account_count}/{max_accounts}`
• Ad Message: {ad_status}
• Cycle Interval: {delay}s
• Advertising Status: {running_status}

╰_╯ Choose an action below to continue"""