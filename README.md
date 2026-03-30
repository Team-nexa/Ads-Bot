## Telegram Ads Bot
A powerful and flexible Telegram bot designed to manage and deliver advertisements efficiently across chats, groups, and channels.

## ★ Features
• 📢 Broadcast ads to multiple users/groups

• 🎯 Targeted advertising system

• ⏱️ Scheduled ad posting

• 📊 Ad performance tracking 

• 🔐 Admin-only control panel

• 🧾 Custom ad formats (text, photo, video, buttons)

• 💾 Database support for users & ads

## Tech Stack

• Python 3.x

• Pyrogram (Telegram Bot API)

• MongoDB (Database)

• Asyncio

# 📦 Installation

#1. Clone the Repository
```git clone https://github.com/yourusername/telegram-ads-bot.git
cd telegram-ads-bot```

#2. Create Virtual Environment
```python -m venv venv
source venv/bin/activate  # Linux
venv\Scripts\activate     # Windows```

#3. Install Requirements
```pip install -r requirements.txt```

#⚙️ Configuration
Create a .env file or edit config.py:
```API_ID=
API_HASH=
BOT_TOKEN=
LOGGER_BOT_TOKEN=
MONGO_URI=
MAX_ACCOUNTS=5
DEFAULT_DELAY=300
PROFILE_LAST_NAME="| By @NexaMeetup"
BIO_TEXT="Ads Managed by @NexaCoders"
START_IMAGE=```

#Run the Bot
```python3 -m Nexa```