from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors.pyromod import ListenerTimeout
import config
import humanize

#===============================================================#

@Client.on_callback_query(filters.regex("^settings$"))
async def settings(client, query):
    total_fsub = len(client.fsub_dict)
    request_enabled = sum(1 for data in client.fsub_dict.values() if data[2])
    timer_enabled = sum(1 for data in client.fsub_dict.values() if data[3] > 0)
    
    total_db_channels = len(getattr(client, 'db_channels', {}))
    primary_db = getattr(client, 'primary_db_channel', client.db)
    
    msg = f"""<blockquote>✦ sᴇᴛᴛɪɴɢs ᴏғ @{client.username} (ᴘᴀɢᴇ 1)</blockquote>
›› **ꜰꜱᴜʙ ᴄʜᴀɴɴᴇʟs:** `{total_fsub}` (ʀᴇǫᴜᴇsᴛ: {request_enabled}, ᴛɪᴍᴇʀ: {timer_enabled})
›› **ᴅʙ ᴄʜᴀɴɴᴇʟs:** `{total_db_channels}` (ᴘʀɪᴍᴀʀʏ: `{primary_db}`)
›› **ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇʀ:** `{client.auto_del}`
›› **ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ:** `{"✓ ᴛʀᴜᴇ" if client.protect else "✗ ꜰᴀʟsᴇ"}`
›› **ᴅɪsᴀʙʟᴇ ʙᴜᴛᴛᴏɴ:** `{"✓ ᴛʀᴜᴇ" if client.disable_btn else "✗ ꜰᴀʟsᴇ"}`
›› **ʀᴇᴘʟʏ ᴛᴇxᴛ:** `{client.reply_text if client.reply_text else 'ɴᴏɴᴇ'}`
›› **ᴀᴅᴍɪɴs:** `{len(client.admins)}`

<blockquote><u>**≡ ᴍᴜʟᴛɪ-sʜᴏʀᴛᴇɴᴇʀ sᴛᴀᴛᴜs:**</u></blockquote>
›› **sʜᴏʀᴛɴᴇʀ 1:** `{config.SHORT_URL_1}`
›› **sʜᴏʀᴛɴᴇʀ 2:** `{config.SHORT_URL_2}`
›› **sʜᴏʀᴛɴᴇʀ 3:** `{config.SHORT_URL_3}`
    """
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('ꜰꜱᴜʙ ᴄʜᴀɴɴᴇʟꜱ', 'fsub'), InlineKeyboardButton('ᴅʙ ᴄʜᴀɴɴᴇʟꜱ', 'db_channels')],
        [InlineKeyboardButton('ᴀᴅᴍɪɴꜱ', 'admins'), InlineKeyboardButton('ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ', 'auto_del')],
        [InlineKeyboardButton('ʜᴏᴍᴇ', 'home'), InlineKeyboardButton('›› ɴᴇxᴛ', 'settings_page_2')]
    ])
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return

#===============================================================#

@Client.on_callback_query(filters.regex("^settings_page_2$"))
async def settings_page_2(client, query):
    total_fsub = len(client.fsub_dict)
    request_enabled = sum(1 for data in client.fsub_dict.values() if data[2])
    timer_enabled = sum(1 for data in client.fsub_dict.values() if data[3] > 0)
    
    total_db_channels = len(getattr(client, 'db_channels', {}))
    primary_db = getattr(client, 'primary_db_channel', client.db)
    
    msg = f"""<blockquote>✦ sᴇᴛᴛɪɴɢs ᴏғ @{client.username} (ᴘᴀɢᴇ 2)</blockquote>
›› **ꜰsᴜʙ ᴄʜᴀɴɴᴇʟs:** `{total_fsub}`
›› **ᴅʙ ᴄʜᴀɴɴᴇʟs:** `{total_db_channels}`
›› **ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ:** `{"✓ ᴛʀᴜᴇ" if client.protect else "✗ ꜰᴀʟsᴇ"}`
›› **ᴅɪsᴀʙʟᴇ ʙᴜᴛᴛᴏɴ:** `{"✓ ᴛʀᴜᴇ" if client.disable_btn else "✗ ꜰᴀʟsᴇ"}`

<blockquote><u>**≡ 1sᴛ sʜᴏʀᴛɴᴇʀ sᴇᴛᴛɪɴɢs:**</u></blockquote>
›› **ᴜʀʟ:** `{config.SHORT_URL_1}`
›› **ᴀᴘɪ:** `{config.SHORT_API_1[:6] if config.SHORT_API_1 else 'ɴᴏᴛ sᴇᴛ'}*****`
›› **ᴛᴜᴛᴏʀɪᴀʟ:** `{config.SHORT_TUT_1}`

<blockquote><u>**≡ 2ɴᴅ sʜᴏʀᴛɴᴇʀ sᴇᴛᴛɪɴɢs:**</u></blockquote>
›› **ᴜʀʟ:** `{config.SHORT_URL_2}`
›› **ᴀᴘɪ:** `{config.SHORT_API_2[:6] if config.SHORT_API_2 else 'ɴᴏᴛ sᴇᴛ'}*****`
›› **ᴛᴜᴛᴏʀɪᴀʟ:** `{config.SHORT_TUT_2}`

<blockquote><u>**≡ 3ʀᴅ sʜᴏʀᴛɴᴇʀ sᴇᴛᴛɪɴɢs:**</u></blockquote>
›› **ᴜʀʟ:** `{config.SHORT_URL_3}`
›› **ᴀᴘɪ:** `{config.SHORT_API_3[:6] if config.SHORT_API_3 else 'ɴᴏᴛ sᴇᴛ'}*****`
›› **ᴛᴜᴛᴏʀɪᴀʟ:** `{config.SHORT_TUT_3}`
    """
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ', 'protect'), InlineKeyboardButton('ᴘʜᴏᴛᴏs', 'photos')],
        [InlineKeyboardButton('ᴛᴇxᴛs', 'texts'), InlineKeyboardButton('🛠️ sʜᴏʀᴛɴᴇʀ sᴇᴛᴛɪɴɢs', 'manage_shortners')],
        [InlineKeyboardButton('‹ ᴘʀᴇᴠ', 'settings'), InlineKeyboardButton('ʜᴏᴍᴇ', 'home')]
    ])
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return

#===============================================================#
# NEW INTERACTIVE CONTROLLER FOR MULTI-SHORTENERS
#===============================================================#

@Client.on_callback_query(filters.regex("^manage_shortners$"))
async def manage_shortners(client, query):
    if not query.from_user.id in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    
    msg = f"""<blockquote>✦ ᴍᴜʟᴛɪ-sʜᴏʀᴛᴇɴᴇʀ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ᴘᴀɴᴇʟ</blockquote>

›› **1sᴛ:** `{config.SHORT_URL_1}`
›› **2ɴᴅ:** `{config.SHORT_URL_2}`
›› **3ʀᴅ:** `{config.SHORT_URL_3}`

__ᴄʟɪᴄᴋ ᴏɴ ᴀɴʏ sʜᴏʀᴛᴇɴᴇʀ ʙᴇʟᴏᴡ ᴛᴏ ᴄʜᴀɴɢᴇ ɪᴛs ᴜʀʟ, ᴀᴘɪ, ᴀɴᴅ sᴇᴘᴀʀᴀᴛᴇ ᴛᴜᴛᴏʀɪᴀʟ ʟɪɴᴋ line-by-line!__"""
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('🔧 sʜᴏʀᴛɴᴇʀ 1', 'edit_short_1'), InlineKeyboardButton('🔧 sʜᴏʀᴛɴᴇʀ 2', 'edit_short_2')],
        [InlineKeyboardButton('🔧 sʜᴏʀᴛɴᴇʀ 3', 'edit_short_3')],
        [InlineKeyboardButton('‹ ʙᴀᴄᴋ', 'settings_page_2')]
    ])
    await query.message.edit_text(msg, reply_markup=reply_markup)

#===============================================================#

@Client.on_callback_query(filters.regex("^edit_short_(1|2|3)$"))
async def edit_specific_shortner(client, query):
    if not query.from_user.id in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    
    num = query.data.split("_")[2]
    url_val = getattr(config, f"SHORT_URL_{num}")
    tut_val = getattr(config, f"SHORT_TUT_{num}")
    
    msg = f"""
    
