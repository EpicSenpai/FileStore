from helper.helper_func import *
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait
import humanize
import asyncio
from config import (
    MESSAGES, MSG_EFFECT, OWNER_ID, 
    SHORT_URL_1, SHORT_API_1, SHORT_TUT_1,
    SHORT_URL_2, SHORT_API_2, SHORT_TUT_2,
    SHORT_URL_3, SHORT_API_3, SHORT_TUT_3
)
from plugins.shortner import get_short
from helper.helper_func import get_messages, force_sub, decode

# Background clean scheduler loop task handler
async def schedule_dynamic_deletion(client: Client, chat_id: int, media_messages: list, banner_msg: Message, transfer_link: str):
    # 30 Minutes structural deletion latency = 1800 seconds
    await asyncio.sleep(1800)
    
    # 1. Purge all media nodes safely from chat history
    for msg in media_messages:
        try:
            await msg.delete()
        except Exception:
            pass

    # 2. Render the short and crisp structural recovery text block with aesthetic small caps
    retrieval_text = (
        "<b>›› ᴘʀᴇᴠɪᴏᴜs ᴍᴇssᴀɢᴇ ᴡᴀs ᴅᴇʟᴇᴛᴇᴅ\n\n"
        "ɪꜰ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ɢᴇᴛ ᴛʜᴇ ꜰɪʟᴇs ᴀɢᴀɪɴ, ᴛʜᴇɴ ᴄʟɪᴄᴋ: • ɢᴇᴛ ꜰɪʟᴇs • "
        "ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴇʟsᴇ ᴄʟᴏsᴇ ᴛʜɪs ᴍᴇssᴀɢᴇ.</b>"
    )
    
    retrieval_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("• ɢᴇᴛ ꜰɪʟᴇs •", callback_data=f"getfiles_{transfer_link}"),
            InlineKeyboardButton("ᴄʟᴏsᴇ •", callback_data="close")
        ]
    ])
    
    try:
        await banner_msg.edit_text(
            text=retrieval_text,
            reply_markup=retrieval_markup
        )
    except Exception:
        try:
            await client.send_message(chat_id=chat_id, text=retrieval_text, reply_markup=retrieval_markup)
        except Exception:
            pass

#===============================================================#

@Client.on_message(filters.command('start') & filters.private)
@force_sub
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id

    present = await client.mongodb.present_user(user_id)
    if not present:
        try:
            await client.mongodb.add_user(user_id)
        except Exception as e:
            client.LOGGER(__name__, client.name).warning(f"Error adding a user:\n{e}")

    is_banned = await client.mongodb.is_banned(user_id)
    if is_banned:
        return await message.reply("<b>✗ ʏᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ʙᴀɴɴᴇᴅ ꜰʀᴏᴍ ᴜsɪɴɢ ᴛʜɪs ʙᴏᴛ!</b>")

    text = message.text
    if len(text) > 7:
        try:
            original_payload = text.split(" ", 1)[1]
            base64_string = original_payload

            is_short_link = False
            if base64_string.startswith("yu3elk"):
                base64_string = base64_string[6:-1]
                is_short_link = True

        except IndexError:
            return await message.reply("<b>✗ ɪɴᴠᴀʟɪᴅ ᴄᴏᴍᴍᴀɴᴅ ꜰᴏʀᴍᴀᴛ.</b>")

        is_user_pro = await client.mongodb.is_pro(user_id)
        shortner_enabled = getattr(client, 'shortner_enabled', True)

        #===============================================================#
        # MONGO TOKEN TRACKING LOGIC (DYNAMIC DEDUCTION & ROTATION)
        #===============================================================#
        if not is_user_pro and user
        
