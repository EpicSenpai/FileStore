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

# Smart Logger wrapper to handle bot.py custom method formatting dynamically
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
PORT = int(os.environ.get("PORT", "7860"))

OWNER_ID = int(os.environ.get("OWNER_ID", "824793853"))
MSG_EFFECT = int(os.environ.get("MSG_EFFECT", "5046509860389126442"))

#===============================================================#
# MULTI-SHORTENER GLOBAL VARIABLES WITH LIVE MUTATION SUPPORT
#===============================================================#

SHORT_URL_1 = os.environ.get("SHORT_URL_1", "")
SHORT_API_1 = os.environ.get("SHORT_API_1", "")
SHORT_TUT_1 = os.environ.get("SHORT_TUT_1", "")

SHORT_URL_2 = os.environ.get("SHORT_URL_2", "")
SHORT_API_2 = os.environ.get("SHORT_API_2", "")
SHORT_TUT_2 = os.environ.get("SHORT_TUT_2", "")

SHORT_URL_3 = os.environ.get("SHORT_URL_3", "")
SHORT_API_3 = os.environ.get("SHORT_API_3", "")
SHORT_TUT_3 = os.environ.get("SHORT_TUT_3", "")

# Legacy compatibility layers
SHORT_URL = SHORT_URL_1
SHORT_API = SHORT_API_1
SHORT_TUT = SHORT_TUT_1

#===============================================================#

SESSION = os.environ.get("SESSION", "")
TOKEN = os.environ.get("TOKEN", "")
API_ID = int(os.environ.get("API_ID", "34310221"))
API_HASH = os.environ.get("API_HASH", "9e18f477424fa6252663d5d6c895470d")
WORKERS = int(os.environ.get("WORKERS", "5"))

DB_URI = os.environ.get("DB_URI", "")
DB_NAME = os.environ.get("DB_NAME", "")

DB_CHANNEL = int(os.environ.get("DB_CHANNEL", ""))
FSUBS = [] 

ADMINS = [int(x) for x in os.environ.get("ADMINS", "824793853").split(",") if x.strip().isdigit()]

DISABLE_BTN = True
PROTECT = False 
AUTO_DEL = 1800

# Fixed Messages Configuration
MESSAGES = {
    "START": "<b><blockquote>›› ʜᴇʏ {mention} ~ </blockquote> <blockquote>ᴛʜᴇ ᴏᴄᴇᴀɴ ᴛᴀᴜɢʜᴛ ᴍᴇ ᴏɴᴇ ᴛʜɪɴɢ — ᴇᴠᴇɴ ᴛʜᴇ ᴅᴇᴇᴘᴇꜱᴛ ꜱɪʟᴇɴᴄᴇ ᴄᴀɴ ʜᴏʟᴅ ᴛʜᴇ ʟᴏᴜᴅᴇꜱᴛ ꜰᴇᴇʟɪɴɢꜱ.</blockquote></b>",
    "FSUB": "<b><blockquote>›› ʜᴇʏ 🫧 ~</blockquote> ‼️ ʏᴏᴜʀ ꜰɪʟᴇ ɪs ʀᴇᴀᴅʏ! ᴋɪɴᴅʟʏ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ɢᴇᴛ ᴀᴄᴄᴇss.</b>",
    "ABOUT": "<b>✦ ᴍʏ ɴᴀᴍᴇ: Rᴇᴢᴇ 🫧 <blockquote expandable>›› ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ: <a href='https://t.me/AuraTube'>ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>\n›› ᴏᴡɴᴇʀ: @EpicSenpai\n›› ʟᴀɴɢᴜᴀɢᴇ: <a href='https://docs.python.org/'>ᴘʏᴛʜᴏɴ 3</a>\n›› ᴅᴀᴛᴀʙᴀsᴇ: <a href='https://www.mongodb.com/docs/'>ᴍᴏɴɢᴏ ᴅʙ</a>\n›› ᴅᴇᴠᴇʟᴏᴘᴇʀ: <a href='https://t.me/SenFlux'>ᴄʟɪᴄᴋ ʜᴇʀᴇ</a></blockquote></b>",
    "REPLY": "", 
    "SHORT_MSG": "<b><blockquote>✦ ʜᴇʏ {user_mention} ~</blockquote> ‼️ ɢᴇᴛ ᴀʟʟ ꜰɪʟᴇs ɪɴ ᴀ sɪɴɢʟᴇ ʟɪɴᴋ ‼️\n\n⌂ ʏᴏᴜʀ ʟɪɴᴋ ɪs ʀᴇᴀᴅʏ, ᴋɪɴᴅʟʏ ᴄʟɪᴄᴋ ᴏɴ ᴏᴘᴇɴ ʟɪɴᴋ ʙᴜᴛᴛᴏɴ..</b>",
    "START_PHOTO": "https://litter.catbox.moe/cq72pc.jpg",
    "FSUB_PHOTO": "https://litter.catbox.moe/w9bw9z.jpg",
    "SHORT_PIC": "https://litter.catbox.moe/q9aqxh.jpg"
}
