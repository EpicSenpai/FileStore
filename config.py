import os
import logging
from logging.handlers import RotatingFileHandler

# Bot Configuration
LOG_FILE_NAME = "bot.log"
PORT = os.environ.get("PORT", "5010")

# GitHub par tokens directly na rakhne ke liye hum unhe environment variables se lenge
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

# Glitch Fix: DB_CHANNEL ko link format se match karne ke liye -100 lagaya hai
DB_CHANNEL = int(os.environ.get("DB_CHANNEL", "-1003819023656"))
FSUBS = [] # Ad/Force sub completely removed!

# Admin IDs list split handler
ADMINS = [int(x) for x in os.environ.get("ADMINS", "824793853,6341").split(",") if x.strip().isdigit()]

# Bot Settings
DISABLE_BTN = True
PROTECT = False # Videos forward allow karne ke liye False rakha hai
AUTO_DEL = 1800

# Messages Configuration (Aapka aesthetic custom font style bina kisi galti ke)
MESSAGES = {
    "START": "<b><blockquote>✦ ʜᴇʏ {mention} ~ </blockquote>\n\nᴛʜᴇ ᴍᴏᴏɴ ᴛᴀᴜɢʜᴛ ᴍᴇ ᴏɴᴇ ᴛʜɪɴɢ — ɴᴏ ᴍᴀᴛᴛᴇʀ ʜᴏᴡ ᴅᴀʀᴋ ɪᴛ ɢᴇᴛs, ʏᴏᴜ sᴛɪʟʟ sʜɪɴᴇ..</b>",
    "FSUB": "<b><blockquote>✦ ʜᴇʏ {mention} ~ </blockquote>\n\nʏᴏᴜʀ ꜰɪʟᴇ ɪs ʀᴇᴀᴅʏ! ᴋɪɴᴅʟʏ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ɢᴇᴛ ᴀᴄᴄᴇss.</b>",
    "ABOUT": "<b><blockquote>✦ ᴍʏ ɴᴀᴍᴇ: {bot_name}\n✦ ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ: <a href='https://t.me/AuraTube'>ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>\n✦ ᴏᴡɴᴇʀ: @EpicSenpai\n✦ ʟᴀɴɢᴜᴀɢᴇ: ᴘʏᴛʜᴏɴ 3\n✦ ʟɪʙʀᴀʀʏ: ᴘʏʀᴏɢʀᴀᴍ ᴠ2\n✦ ᴅᴀᴛᴀʙᴀsᴇ: ᴍᴏɴɢᴏ ᴅʙ\n✦ ᴅᴇᴠᴇʟᴏᴘᴇʀ: @EpicSenpai</blockquote></b>",
    "REPLY": "", # Ads completely blocked
    "SHORT_MSG": "<b><blockquote>✦ ʜᴇʏ {user_mention} × </blockquote>\n\n‼️ ɢᴇᴛ ᴀʟʟ ꜰɪʟᴇs ɪɴ ᴀ sɪɴɢʟᴇ ʟɪɴᴋ ‼️\n\n⌂ ʏᴏᴜʀ ʟɪɴᴋ ɪs ʀᴇᴀᴅʏ, ᴋɪɴᴅʟʏ ᴄʟɪᴄᴋ ᴏɴ ᴏᴘᴇɴ ʟɪɴᴋ ʙᴜᴛᴛᴏɴ..</b>",
    "START_PHOTO": "https://litter.catbox.moe/q9aqxh.jpg",
    "FSUB_PHOTO": "https://litter.catbox.moe/w9bw9z.jpg",
    "SHORT_PIC": "https://litter.catbox.moe/q9aqxh.jpg"
}
