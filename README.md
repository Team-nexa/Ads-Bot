# Telegram Ads Bot

A powerful and flexible Telegram bot designed to manage and deliver advertisements efficiently across chats, groups, and channels.

---

## ★ Features

- 📢 Broadcast ads to multiple users/groups  
- 🎯 Targeted advertising system  
- ⏱️ Scheduled ad posting  
- 📊 Ad performance tracking  
- 🔐 Admin-only control panel  
- 🧾 Custom ad formats (text, photo, video, buttons)  
- 💾 Database support for users & ads  

---

## 🛠 Tech Stack

- Python 3.x  
- Pyrogram (Telegram Bot API)  
- MongoDB (Database)  
- Asyncio  

---

## 📦 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/telegram-ads-bot.git
cd telegram-ads-bot
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

Activate it:

**Linux / Mac**
```bash
source venv/bin/activate
```

**Windows**
```bash
venv\Scripts\activate
```

### 3. Install Requirements
```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

Create a `.env` file or edit `config.py`:

```env
API_ID=
API_HASH=
BOT_TOKEN=
LOGGER_BOT_TOKEN=
MONGO_URI=

MAX_ACCOUNTS=5
DEFAULT_DELAY=300

PROFILE_LAST_NAME="| By @NexaMeetup"
BIO_TEXT="Ads Managed by @NexaCoders"

START_IMAGE=
```

---

## ▶️ Run the Bot
```bash
python3 -m Nexa
```

---

## 📁 Project Structure

```
telegram-ads-bot/
│── Nexa/
│   ├── __init__.py
│   ├── modules/
│   ├── utils/
│   └── database/
│
│── config.py
│── requirements.txt
│── README.md
```

---

## 🔒 Notes

- Make sure your bot is **admin in channels/groups** before broadcasting  
- Keep your `.env` file **private**  
- Use a **valid MongoDB URI**  

---

## ❤️ Credits

- 👑 Developed by **Team Nexa**  
- 🔗 https://t.me/NexaCoders  

---

## 📢 Support

- 📣 Channel: https://t.me/NexaCoders  
- 💬 Chat: https://t.me/NexaMeetup  

---

## 📜 License

This project is licensed under the **MIT License**.