from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message, InputMediaPhoto
import config
import re
import base64
from plugins.shortner import get_short
from database import db  # Aapka jo bhi main database import module ho

#===============================================================#
# 🛠️ HELPER FUNCTIONS: ENCODING / DECODING LAYER FOR FILE ID
#===============================================================#

def decode_data(data: str) -> str:
    try:
        data = data.encode('ascii')
        rem = len(data) % 4
        if rem > 0:
            data += b"=" * (4 - rem)
        return base64.urlsafe_b64decode(data).decode('ascii')
    except Exception:
        return ""

#===============================================================#
# 🚀 CORE ROUTER FOR /START COMMAND (WITH FILE RETRIEVAl & SHORTLINK)
#===============================================================#

@Client.on_message(filters.command("start") & filters.private)
async def start_command_handler(client: Client, message: Message):
    user_id = message.from_user.id
    text = message.text
    
    # 1. Base Welcome Dashboard (Agar simple /start command ho bina kisi file query ke)
    if len(text.split()) == 1:
        buttons = [
            [InlineKeyboardButton("• ᴀʙᴏᴜᴛ", callback_data="ABOUT"), InlineKeyboardButton("ᴄʟᴏsᴇ •", callback_data='close')]
        ]
        if user_id in client.admins:
            buttons.insert(0, [InlineKeyboardButton("• sᴇᴛᴛɪɴɢs •", callback_data="settings")])
            
        start_caption = config.MESSAGES.get('START', '').format(
            first=message.from_user.first_name,
            last=message.from_user.last_name or "",
            username=None if not message.from_user.username else '@' + message.from_user.username,
            mention=message.from_user.mention,
            id=user_id
        )
        
        start_photo = config.MESSAGES.get("START_PHOTO", "")
        if start_photo and start_photo != "None":
            return await message.reply_photo(photo=start_photo, caption=start_caption, reply_markup=InlineKeyboardMarkup(buttons))
        else:
            return await message.reply_text(text=start_caption, reply_markup=InlineKeyboardMarkup(buttons))

    # 2. Dynamic File Retrieval Layer (Agar query me file base64 data parameter ho)
    query_data = text.split()[1]
    decoded_string = decode_data(query_data)
    
    if not decoded_string:
        return await message.reply_text("<b>✗ ɪɴᴠᴀʟɪᴅ / sᴇᴄᴜʀᴇ ʟɪɴᴋ ᴄᴏʀʀᴜᴘᴛᴇᴅ!</b>")
        
    # Checking for multi-channel database parsing structure
    parts = decoded_string.split("_")
    if len(parts) < 2:
        return await message.reply_text("<b>✗ ʟɪɴᴋ sᴛʀᴜᴄᴛᴜʀᴇ ɴot sᴜᴘᴘᴏʀᴛᴇᴅ!</b>")
        
    target_channel_id = int(parts[0])
    target_message_id = int(parts[1])
    
    # Check if the user has verified the shortlink token bypass rule
    user_verified = await client.mongodb.is_user_verified(user_id) # dynamic database validation
    
    if not user_verified and user_id not in client.admins:
        # Generate the verified shortlink layer token dynamically using multi-shortener settings
        # It picks config configuration settings automatically
        original_link = f"https://t.me/{client.username}?start={query_data}"
        bypass_short_url = get_short(original_link, client)
        
        tutorial_link = config.MESSAGES.get('SHORT_TUT', 'https://t.me/How_To_Open_Shortners')
        short_msg = config.MESSAGES.get('SHORT_MSG', '<blockquote><b>⚠️ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ʀᴇǫᴜɪʀᴇᴅ!</b></blockquote>\n\n›› ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴠᴇʀɪꜰʏ ᴛᴏ ᴀᴄᴄᴇss ʏᴏᴜʀ ꜰɪʟᴇ.\n›› ᴄʟɪᴄᴋ ᴏɴ ʙʏᴘᴀss ʟɪɴᴋ ʙᴇʟᴏᴡ.').format(
            mention=message.from_user.mention,
            id=user_id
        )
        
        short_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton('🚀 ʙʏᴘᴀss / ᴠᴇʀɪꜰʏ ʟɪɴᴋ', url=bypass_short_url)],
            [InlineKeyboardButton('📖 ʜᴏᴡ ᴛᴏ ᴏᴘᴇɴ / ᴛᴜᴛᴏʀɪᴀʟ', url=tutorial_link)]
        ])
        
        short_pic = config.MESSAGES.get('SHORT_PIC', '')
        if short_pic and short_pic != "None":
            return await message.reply_photo(photo=short_pic, caption=short_msg, reply_markup=short_markup)
        else:
            return await message.reply_text(text=short_msg, reply_markup=short_markup)

    # 3. File Delivery Mechanism (If validated successfully or user is admin)
    try:
        # Fetch packet payload using primary db context template
        copied_msg = await client.copy_message(
            chat_id=message.chat.id,
            from_chat_id=target_channel_id,
            message_id=target_message_id,
            protect_content=client.protect
        )
        
        # Auto delete handler if dynamic timer loop is active (> 0)
        if client.auto_del > 0:
            client.loop.create_task(client.delete_links(copied_msg, client.auto_del))
            
    except Exception as e:
        await message.reply_text(f"<b>✗ ꜰɪʟᴇ ᴅᴇʟɪᴠᴇʀʏ ꜰᴀɪʟᴇᴅ!</b>\n\n›› ᴇʀʀᴏʀ: <code>{str(e)}</code>")
        
