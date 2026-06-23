import os
import logging
from logging.handlers import RotatingFileHandler

# Standard logging configuration setup
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    handlers=[
        RotatingFileHandler("bot.log", maxBytes=50000000, backupCount=10),
        logging.StreamHandler()
    ]
)

# Smart Logger wrapper wrapper to handle bot.py custom method formatting dynamically
class SmartLogger:
    def __init__(self, name=__name__):
        self._logger = logging.getLogger(name)
    
    def __call__(self, *args, **kwargs):
        return self._logger
        
    def __getattr__(self, name):
        return getattr(self._logger, name)

LOGGER = SmartLogger()

# Bot Configuration
LOG_FILE_NAME = "bot.log"
PORT = os.environ.get("PORT", "5010")

OWNER_ID = int(os.environ.get("OWNER_ID", "824793853"))
MSG_EFFECT = int(os.environ.get("MSG_EFFECT", "5046509860389126442"))

SHORT_URL = os.environ.get("SHORT_URL", "") 
SHORT_API = os.environ.get("SHORT_API", "")
SHORT_TUT = os.environ.get("SHORT_TUT", "")

SESSION = os.environ.get("SESSION", "rezebot")
TOKEN = os.environ.get("TOKEN", "8743100938:AAGhqbQ4M9uKPKIwjNht9AZ")
API_ID = int(os.environ.get("API_ID", "34310221"))
API_HASH = os.environ.get("API_HASH", "9e18f477424fa6252663d5d6c895470d")
WORKERS = int(os.environ.get("WORKERS", "5"))

DB_URI = os.environ.get("DB_URI", "mongodb+srv://rezebot:bXtk6z31xL")
DB_NAME = os.environ.get("DB_NAME", "rezebot")

DB_CHANNEL = int(os.environ.get("DB_CHANNEL", "-1003819023656"))
FSUBS = [] # Completely Removed

ADMINS = [int(x) for x in os.environ.get("ADMINS", "824793853,6341").split(",") if x.strip().isdigit()]

DISABLE_BTN = True
PROTECT = False 
AUTO_DEL = 1800

# Fixed Messages Configuration without 'Copy Code' glitch and fully functional About button
MESSAGES = {
    "START": "<b><blockquote>✦ ʜᴇʏ {mention} ~ </blockquote> <blockquote>ᴛʜᴇ ᴍᴏᴏɴ ᴛᴀᴜɢʜᴛ ᴍᴇ ᴏɴᴇ ᴛʜɪɴɢ — ɴᴏ ᴍᴀᴛᴛᴇʀ ʜᴏᴡ ᴅᴀʀᴋ ɪᴛ ɢᴇᴛs, ʏᴏᴜ sᴛɪʟʟ sʜɪɴᴇ..</blockquote></b>",
    "FSUB": "<b><blockquote>✦ ʜᴇʏ {mention} ~</blockquote> ʏᴏᴜʀ ꜰɪʟᴇ ɪs ʀᴇᴀᴅʏ! ᴋɪɴᴅʟʏ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ɢᴇᴛ ᴀᴄᴄᴇss.</b>",
    "ABOUT": "<b>✦ ᴍʏ ɴᴀᴍᴇ: {bot_name} <blockquote>✦ ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ: <a href='https://t.me/PRIME_SMP'>ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>\n✦ ᴏᴡɴᴇʀ: @EpicSenpai\n✦ ʟᴀɴɢᴜᴀɢᴇ: ᴘʏᴛʜᴏɴ 3\n✦ ʟɪʙʀᴀʀʏ: ᴘʏʀᴏɢʀᴀᴍ ᴠ2\n✦ ᴅᴀᴛᴀʙᴀsᴇ: ᴍᴏɴɢᴏ ᴅʙ\n✦ ᴅᴇᴠᴇʟᴏᴘᴇʀ: @EpicSenpai</blockquote></b>",
    "REPLY": "", 
    "SHORT_MSG": "<b><blockquote>✦ ʜᴇʏ {user_mention} ~</blockquote> ‼️ ɢᴇᴛ ᴀʟʟ ꜰɪʟᴇs ɪɴ ᴀ sɪɴɢʟᴇ ʟɪɴᴋ ‼️\n\n⌂ ʏᴏᴜʀ ʟɪɴᴋ ɪs ʀᴇᴀᴅʏ, ᴋɪɴᴅʟʏ ᴄʟɪᴄᴋ ᴏɴ ᴏᴘᴇɴ ʟɪɴᴋ ʙᴜᴛᴛᴏɴ..</b>",
    "START_PHOTO": "https://litter.catbox.moe/q9aqxh.jpg",
    "FSUB_PHOTO": "https://litter.catbox.moe/w9bw9z.jpg",
    "SHORT_PIC": "https://litter.catbox.moe/q9aqxh.jpg"
}
