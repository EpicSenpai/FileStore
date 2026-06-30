import requests
import random
import string
import config
from config import MESSAGES
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram.errors.pyromod import ListenerTimeout

# ✅ In-memory cache
shortened_urls_cache = {}

def generate_random_alphanumeric():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(8))

def get_short(url, client):
    # Check if shortner is enabled
    shortner_enabled = getattr(client, 'shortner_enabled', True)
    if not shortner_enabled:
        return url  # Return original URL if shortner is disabled

    # Step 2: Check cache
    if url in shortened_urls_cache:
        return shortened_urls_cache[url]

    try:
        alias = generate_random_alphanumeric()
        # Dynamic variable mapping based on current rotation index settings
        short_url = getattr(client, 'short_url', config.SHORT_URL_1)
        short_api = getattr(client, 'short_api', config.SHORT_API_1)
        
        api_url = f"https://{short_url}/api?api={short_api}&url={url}&alias={alias}"
        response = requests.get(api_url, timeout=10)
        rjson = response.json()

        if rjson.get("status") == "success" and response.status_code == 200:
            short_url_res = rjson.get("shortenedUrl", url)
            shortened_urls_cache[url] = short_url_res
            return short_url_res
    except Exception as e:
        print(f"[Shortener Error] {e}")

    return url  # fallback

#===============================================================#

@Client.on_message(filters.command('shortner') & filters.private)
async def shortner_command(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    await shortner_panel(client, message)

#===============================================================#

async def shortner_panel(client, query_or_message):
    shortner_enabled = getattr(client, 'shortner_enabled', True)
    enabled_text = "✓ ᴇɴᴀʙʟᴇᴅ" if shortner_enabled else "✗ ᴅɪsᴀʙʟᴇᴅ"
    toggle_text = "✗ ᴛᴜʀɴ ᴏғғ" if shortner_enabled else "✓ ᴛᴜʀɴ ᴏɴ"
    
    # 3 Shorteners core tracking data extraction layer
    url1 = getattr(config, 'SHORT_URL_1', 'None')
    url2 = getattr(config, 'SHORT_URL_2', 'None')
    url3 = getattr(config, 'SHORT_URL_3', 'None')
    
    status1 = "🟢 ᴏɴ" if getattr(config, 'SHORT_STATUS_1', True) else "🔴 ᴏғғ"
    status2 = "🟢 ᴏɴ" if getattr(config, 'SHORT_STATUS_2', True) else "🔴 ᴏғғ"
    status3 = "🟢 ᴏɴ" if getattr(config, 'SHORT_STATUS_3', True) else "🔴 ᴏғғ"
    
    msg = f"<b>◍ ᴍᴜʟᴛɪ sʜᴏʀᴛɴᴇʀ sᴇᴛᴛɪɴɢs</b>\n\n" \
          f"<b><u>ᴄᴜʀʀᴇɴᴛ sᴇᴛᴛɪɴɢs:</u></b>\n" \
          f"<blockquote>›› **ɢʟᴏʙᴀʟ sᴛᴀᴛᴜs:** {enabled_text}\n" \
          f"›› **ꜱʜᴏʀᴛɴᴇʀ 1:** `{url1}` [ {status1} ]\n" \
          f"›› **ꜱʜᴏʀᴛɴᴇʀ 2:** `{url2}` [ {status2} ]\n" \
          f"›› **ꜱʜᴏʀᴛɴᴇʀ 3:** `{url3}` [ {status3} ]</blockquote>\n\n" \
          f"<b><blockquote>≡ ᴜsᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ᴛᴏ ᴍᴀɴᴀɢᴇ ᴀɴᴅ ᴄᴏɴꜰɪɢᴜʀᴇ ʏᴏᴜʀ sʜᴏʀᴛɴᴇer sᴇᴛᴛɪɴɢs!</blockquote></b>"
    
    # Kept your exact structural buttons layout intact but expanded for 3 nodes control safely
    buttons = [
        [InlineKeyboardButton(f'• {toggle_text} ꜱʜᴏʀᴛɴᴇʀ •', 'toggle_shortner')],
        [InlineKeyboardButton('• ᴍᴀɴᴀɢᴇ sʜᴏʀᴛ 1 •', 'edit_short_1'), InlineKeyboardButton('• ᴍᴀɴᴀɢᴇ sʜᴏʀᴛ 2 •', 'edit_short_2')],
        [InlineKeyboardButton('• ᴍᴀɴᴀɢᴇ sʜᴏʀᴛ 3 •', 'edit_short_3')]
    ]
    
    if hasattr(query_or_message, 'message'):
        buttons.append([InlineKeyboardButton('◂ ʙᴀᴄᴋ ᴛᴏ sᴇᴛᴛɪɴɢs', 'settings')])
        
    reply_markup = InlineKeyboardMarkup(buttons)
    image_url = MESSAGES.get("SHORT", "https://litter.catbox.moe/q9aqxh.jpg")
    
    if hasattr(query_or_message, 'message'):
        await query_or_message.message.edit_media(
            media=InputMediaPhoto(media=image_url, caption=msg),
            reply_markup=reply_markup
        )
    else:
        await query_or_message.reply_photo(photo=image_url, caption=msg, reply_markup=reply_markup)

#===============================================================#

@Client.on_callback_query(filters.regex("^shortner$"))
async def shortner_callback(client, query):
    if not query.from_user.id in client.admins:
        return await query.answer('❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    await query.answer()
    await shortner_panel(client, query)

#===============================================================#

@Client.on_callback_query(filters.regex("^toggle_shortner$"))
async def toggle_shortner(client: Client, query: CallbackQuery):
    if not query.from_user.id in client.admins:
        return await query.answer('❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
        
    current_status = getattr(client, 'shortner_enabled', True)
    new_status = not current_status
    client.shortner_enabled = new_status
    
    await client.mongodb.set_shortner_status(new_status)
    status_text = "ᴇɴᴀʙʟᴇᴅ" if new_status else "ᴅɪsᴀʙʟᴇᴅ"
    await query.answer(f"✓ ꜱʜᴏʀᴛɴᴇʀ {status_text}!")
    await shortner_panel(client, query)
    
