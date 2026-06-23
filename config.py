import os
import logging
from logging.handlers import RotatingFileHandler

# Bot Configuration
LOG_FILE_NAME = "bot.log"
PORT = os.environ.get("PORT", "5010")

# GitHub par tokens directly na rakhne ke liye hum unhe environment variables se fetch kar rahe hain
OWNER_ID = int(os.environ.get("OWNER_ID", "8247593853")) 
MSG_EFFECT = int(os.environ.get("MSG_EFFECT", "5046509860389126442"))

SHORT_URL = os.environ.get("SHORT_URL", "gplinks.com") # shortner url 
SHORT_API = os.environ.get("SHORT_API", "540e6d65d2851a9c645d0eafb573535af3d33943") 
SHORT_TUT = os.environ.get("SHORT_TUT", "https://t.me/How_To_Open_Shortners")

SESSION = os.environ.get("SESSION", "rezebot")
TOKEN = os.environ.get("TOKEN", "8743100938:AAGhqbQ4M9uKPKIwjNht9AZX4gp0GsiFrnw")
API_ID = int(os.environ.get("API_ID", "34310221"))
API_HASH = os.environ.get("API_HASH", "9e18f477424fa6252663d5d6c895253a")
WORKERS = int(os.environ.get("WORKERS", "5"))

DB_URI = os.environ.get("DB_URI", "mongodb+srv://rezebot:bXtk6z31xLZlLxQW@cluster0.cw2xujb.mongodb.net/rezebot?appName=Cluster0")
DB_NAME = os.environ.get("DB_NAME", "rezebot")

# Glitch Fix: DB_CHANNEL ko link format se match karne ke liye -100 ke bina load kiya hai
DB_CHANNEL = int(os.environ.get("DB_CHANNEL", "-3819023656"))
FSUBS = [[int(os.environ.get("FSUB_CHANNEL", "-1003819023656")), True, 10]] 

# Admin IDs list split handler
ADMINS = [int(x) for x in os.environ.get("ADMINS", "8247593853,6341576569").split(",")]

# Bot Settings
DISABLE_BTN = True
PROTECT = False # Videos forward allow karne ke liye False rakha hai
AUTO_DEL = 1800

# Messages Configuration (Aapka aesthetic custom font style)
MESSAGES = {
    "START": "<b><blockquote>›› ʜᴇʏ {mention} ~ </blockquote>  <blockquote>ᴛʜᴇ ᴍᴏᴏɴ ᴛᴀᴜɢʜᴛ ᴍᴇ ᴏɴᴇ ᴛʜɪɴ — ɴᴏ ᴍᴀᴛᴛᴇ r ʜᴏᴡ ᴅᴀʀᴋ ɪᴛ ɢᴇᴛs, ʏᴏᴜ sᴛɪʟʟ sʜɪɴᴇ..</blockquote></b>",
    "FSUB": "<b><blockquote>›› ʜᴇʏ ×</blockquote>\n  ʏᴏᴜʀ ғɪʟᴇ ɪs ʀᴇᴀᴅʏ ‼️ ʟᴏᴏᴋs ʟɪᴋᴇ ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ sᴜʙsᴄʀɪʙᴇ ᴅ ᴛᴏ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ʏᴇᴛ, sᴜʙsᴄʀɪʙᴇ ɴᴏᴡ ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ғɪʟᴇs</b>",
    "ABOUT": "<b>›› ᴍʏ ɴᴀᴍᴇ: {bot_name} \n <blockquote expandable>›› ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ: <a href='https://t.me/AuraTube'>Cʟɪᴄᴋ ʜᴇ rᴇ</a> \n›› ᴏᴡɴᴇ r: @EpicSenpai\n›› ʟᴀɴɢᴜᴀɢᴇ: <a href='https://docs.python.org/3/'>Pʏᴛʜᴏɴ 3</a> \n›› ʟɪʙʀᴀʀʏ: <a href='https://docs.pyrogram.org/'>Pʏʀᴏɢʀᴀᴍ ᴠ2</a> \n›› ᴅᴀᴛᴀʙᴀsᴇ: <a href='https://www.mongodb.com/docs/'>Mᴏɴɢᴏ ᴅʙ</a> \n›› ᴅᴇᴠᴇʟᴏᴘᴇ r: @EpicSenpai</b></blockquote>",
    "REPLY": "<b>For More Join - @SpicyVerse</b>",
    "SHORT_MSG": "<b>📊 ʜᴇʏ {user_mention} \n\n‼️ ɢᴇᴛ ᴀʟʟ ꜰɪʟᴇꜱ ɪɴ ᴀ ꜱɪɴɢʟᴇ ʟɪɴᴋ ‼️\n\n ⌯ ʏᴏᴜʀ ʟɪɴᴋ ɪꜱ ʀᴇᴀᴅʏ, ᴋɪɴᴅʟʏ ᴄʟɪᴄᴋ ᴏɴ ᴏᴘᴇɴ ʟɪɴᴋ ʙᴜᴛᴛᴏɴ..</b>",
    "START_PHOTO": "https://litter.catbox.moe/q9aqxh.jpg",
    "FSUB_PHOTO": "https://litter.catbox.moe/w9bw9z.jpg",
    "SHORT_PIC": "https://litter.catbox.moe/2zd2uk.jpg",
    "SHORT": "https://litter.catbox.moe/1y3cjr.jpg"
}

def LOGGER(name: str, client_name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    formatter = logging.Formatter(
        f"[%(asctime)s - %(levelname)s] - {client_name} - %(name)s - %(message)s",
        datefmt='%d-%b-%y %H:%M:%S'
    )
    file_handler = RotatingFileHandler(LOG_FILE_NAME, maxBytes=50_000_000, backupCount=10)
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
    
