from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
import config

#===============================================================#
# ⚙️ REZE CORE NAVIGATION GRID RENDERING ENGINE (ZERO ERROR MULTI-SHORTENER)
#===============================================================#

async def get_settings_menu_layout(client, page=1):
    total_fsub = len(client.fsub_dict)
    request_enabled = sum(1 for data in client.fsub_dict.values() if data[2])
    timer_enabled = sum(1 for data in client.fsub_dict.values() if data[3] > 0)
    
    total_db_channels = len(getattr(client, 'db_channels', {}))
    primary_db = getattr(client, 'primary_db_channel', client.db)

    if page == 1:
        msg = f"<b>◍ sᴇᴛᴛɪɴɢs ᴏꜰ @{client.username} (ᴘᴀɢᴇ 1)</b>\n\n" \
              f"<b>›› ꜰsᴜʙ ᴄʜᴀɴɴᴇʟs:</b> <code>{total_fsub}</code> (ʀᴇǫᴜᴇsᴛ: {request_enabled}, ᴛɪᴍᴇʀ: {timer_enabled})\n" \
              f"<b>›› ᴅʙ ᴄʜᴀɴɴᴇʟs:</b> <code>{total_db_channels}</code> (ᴘʀɪᴍᴀʀʏ: <code>{primary_db}</code>)\n" \
              f"<b>›› ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇʀ:</b> <code>{client.auto_del}s</code>\n" \
              f"<b>›› ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ:</b> <code>{'✓ ᴛʀᴜᴇ' if client.protect else '✗ ꜰᴀʟsᴇ'}</code>\n" \
              f"<b>›› ᴅɪsᴀʙʟᴇ ʙᴜᴛᴛᴏɴ:</b> <code>{'✓ ᴛʀᴜᴇ' if client.disable_btn else '✗ ꜰᴀʟsᴇ'}</code>\n" \
              f"<b>›› ʀᴇᴘʟʏ ᴛᴇxᴛ:</b> <code>{client.reply_text if client.reply_text else '¼ ɴᴏɴᴇ'}</code>\n" \
              f"<b>›› ᴀᴅᴍɪɴs:</b> <code>{len(client.admins)}</code>\n\n" \
              f"<b><u>≡ ᴍᴜʟᴛɪ-sʜᴏʀᴛᴇɴᴇʀ sᴛᴀᴛᴜs:</u></b>\n" \
              f"<b>›› sʜᴏʀᴛɴᴇʀ 1:</b> <code>{getattr(config, 'SHORT_URL_1', 'None')}</code> [ <code>{'🟢 ᴏɴ' if getattr(config, 'SHORT_STATUS_1', True) else '🔴 ᴏғғ'}</code> ]\n" \
              f"<b>›› sʜᴏʀᴛɴᴇer 2:</b> <code>{getattr(config, 'SHORT_URL_2', 'None')}</code> [ <code>{'🟢 ᴏɴ' if getattr(config, 'SHORT_STATUS_2', True) else '🔴 ᴏғғ'}</code> ]\n" \
              f"<b>›› sʜᴏʀᴛɴᴇer 3:</b> <code>{getattr(config, 'SHORT_URL_3', 'None')}</code> [ <code>{'🟢 ᴏɴ' if getattr(config, 'SHORT_STATUS_3', True) else '🔴 ᴏғғ'}</code> ]"
              
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton('ꜰsᴜʙ ᴄʜᴀɴɴᴇʟs', 'fsub'), InlineKeyboardButton('ᴅʙ ᴄʜᴀɴɴᴇʟs', 'db_channels')],
            [InlineKeyboardButton('ᴀᴅᴍɪɴs', 'admins'), InlineKeyboardButton('ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ', 'auto_del')],
            [InlineKeyboardButton('ʜᴏᴍᴇ', 'home'), InlineKeyboardButton('›› ɴᴇxᴛ', 'settings_page_2')]
        ])
    else:
        msg = f"<b>◍ sᴇᴛᴛɪɴɢs ᴏꜰ @{client.username} (ᴘᴀɢᴇ 2)</b>\n\n" \
              f"<b>›› ꜰsᴜʙ ᴄʜᴀɴɴᴇʟs:</b> <code>{total_fsub}</code>\n" \
              f"<b>›› ᴅʙ ᴄʜᴀɴɴᴇʟs:</b> <code>{total_db_channels}</code>\n" \
              f"<b>›› ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ:</b> <code>{'✓ ᴛʀᴜᴇ' if client.protect else '✗ ꜰᴀʟsᴇ'}</code>\n" \
              f"<b>›› ᴅɪsᴀʙʟᴇ ʙᴜᴛᴛᴏɴ:</b> <code>{'✓ ᴛʀᴜᴇ' if client.disable_btn else '✗ ꜰᴀʟsᴇ'}</code>\n\n" \
              f"<b><u>≡ 1sᴛ sʜᴏʀᴛᴇɴᴇer sᴇᴛᴛɪɴɢs:</u></b>\n" \
              f"›› <b>sᴛᴀᴛᴜs:</b> <code>{'🟢 ᴇɴᴀʙʟᴇᴅ' if getattr(config, 'SHORT_STATUS_1', True) else '🔴 ᴅɪsᴀʙʟᴇᴅ'}</code>\n" \
              f"›› <b>ᴜʀʟ:</b> <code>{getattr(config, 'SHORT_URL_1', 'None')}</code>\n\n" \
              f"<b><u>≡ 2ɴᴅ sʜᴏʀᴛᴇɴᴇer sᴇᴛᴛɪɴɢs:</u></b>\n" \
              f"›› <b>sᴛᴀᴛᴜs:</b> <code>{'🟢 ᴇɴᴀʙʟᴇᴅ' if getattr(config, 'SHORT_STATUS_2', True) else '🔴 ᴅɪsᴀʙʟᴇᴅ'}</code>\n" \
              f"›› <b>ᴜʀʟ:</b> <code>{getattr(config, 'SHORT_URL_2', 'None')}</code>\n\n" \
              f"<b><u>≡ 3ʀᴅ sʜᴏʀᴛᴇɴᴇer sᴇᴛᴛɪɴɢs:</u></b>\n" \
              f"›› <b>sᴛᴀᴛᴜs:</b> <code>{'🟢 ᴇɴᴀʙʟᴇᴅ' if getattr(config, 'SHORT_STATUS_3', True) else '🔴 ᴅɪsᴀʙʟᴇᴅ'}</code>\n" \
              f"›› <b>ᴜʀʟ:</b> <code>{getattr(config, 'SHORT_URL_3', 'None')}</code>"
              
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton('ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ', 'protect'), InlineKeyboardButton('ᴘʜᴏᴛᴏs', 'photos')],
            [InlineKeyboardButton('ᴛᴇxᴛs', 'texts'), InlineKeyboardButton('🛠️ sʜᴏʀᴛɴᴇer sᴇᴛᴛɪɴɢs', 'shortner')],
            [InlineKeyboardButton('‹ ᴘʀᴇᴠ', 'settings'), InlineKeyboardButton('ʜᴏᴍᴇ', 'home')]
        ])
        
    return msg, markup

#===============================================================#
# 🚀 REAL TEXT COMMAND /SETTINGS INTERACTION HANDLER
#===============================================================#

@Client.on_message(filters.command("settings") & filters.private)
async def settings_text_command(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    
    msg, markup = await get_settings_menu_layout(client, page=1)
    image_url = config.MESSAGES.get("START_PHOTO", "https://litter.catbox.moe/q9aqxh.jpg")
    await message.reply_photo(photo=image_url, caption=msg, reply_markup=markup)

#===============================================================#
# 📲 GLOBAL CALLBACK INTERFACES MANAGERS
#===============================================================#

@Client.on_callback_query(filters.regex("^settings$"))
async def settings_callback(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    await query.answer()
    msg, markup = await get_settings_menu_layout(client, page=1)
    await query.message.edit_caption(caption=msg, reply_markup=markup)

@Client.on_callback_query(filters.regex("^settings_page_2$"))
async def settings_page_2_callback(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    await query.answer()
    msg, markup = await get_settings_menu_layout(client, page=2)
    await query.message.edit_caption(caption=msg, reply_markup=markup)

#===============================================================#

@Client.on_callback_query(filters.regex("^home$"))
async def back_to_home_callback(client: Client, query: CallbackQuery):
    await query.answer("↩️ Returning back to home dashboard...")
    user_id = query.from_user.id
    
    buttons = [[InlineKeyboardButton("• ᴀʙᴏᴜᴛ", callback_data="ABOUT"), InlineKeyboardButton("ᴄʟᴏsᴇ •", callback_data='close')]]
    if user_id in client.admins:
        buttons.insert(0, [InlineKeyboardButton("• ꜱᴇᴛᴛɪɴɢs •", callback_data="settings")])
        
    start_caption = config.MESSAGES.get('START', '').format(
        first=query.from_user.first_name,
        last=query.from_user.last_name or "",
        username=None if not query.from_user.username else '@' + query.from_user.username,
        mention=query.from_user.mention,
        id=user_id
    )
    
    await query.message.edit_media(
        media=InputMediaPhoto(media=config.MESSAGES.get("START_PHOTO", ""), caption=start_caption),
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex("^ABOUT$"))
async def render_about_callback_query(client: Client, query: CallbackQuery):
    await query.answer("ℹ️ Loading about documentation details...")
    about_text = config.MESSAGES.get('ABOUT', '').format(bot_name=client.username)
    back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data="home")]])
    await query.message.edit_caption(caption=about_text, reply_markup=back_markup)

@Client.on_callback_query(filters.regex("^close$"))
async def close_panel_callback_query(client: Client, query: CallbackQuery):
    await query.answer("🗑️ Interface closed.")
    await query.message.delete()
    
