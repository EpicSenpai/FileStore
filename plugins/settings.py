from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram.errors.pyromod import ListenerTimeout
import config

#===============================================================#
# ⚙️ MAIN SETTINGS INTERFACE RENDERING ENGINE (PHOTO SUPPORT)
#===============================================================#

async def render_settings_view(client, query_or_message, page=1, edit=True):
    total_fsub = len(client.fsub_dict)
    request_enabled = sum(1 for data in client.fsub_dict.values() if data[2])
    timer_enabled = sum(1 for data in client.fsub_dict.values() if data[3] > 0)
    
    total_db_channels = len(getattr(client, 'db_channels', {}))
    primary_db = getattr(client, 'primary_db_channel', client.db)
    
    image_url = config.MESSAGES.get("START_PHOTO", "https://litter.catbox.moe/q9aqxh.jpg")

    if page == 1:
        msg = f"<b>◍ sᴇᴛᴛɪɴɢs ᴏꜰ @{client.username} (ᴘᴀɢᴇ 1)</b>\n\n" \
              f"<b>›› ꜰsᴜʙ ᴄʜᴀɴɴᴇʟs:</b> <code>{total_fsub}</code> (ʀᴇǫᴜᴇsᴛ: {request_enabled}, ᴛɪᴍᴇʀ: {timer_enabled})\n" \
              f"<b>›› ᴅʙ ᴄʜᴀɴɴᴇʟs:</b> <code>{total_db_channels}</code> (ᴘʀɪᴍᴀʀʏ: <code>{primary_db}</code>)\n" \
              f"<b>›› ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇʀ:</b> <code>{client.auto_del}s</code>\n" \
              f"<b>›› ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ:</b> <code>{'✓ ᴛʀᴜᴇ' if client.protect else '✗ ꜰᴀʟsᴇ'}</code>\n" \
              f"<b>›› ᴅɪsᴀʙʟᴇ ʙᴜᴛᴛᴏɴ:</b> <code>{'✓ ᴛʀᴜᴇ' if client.disable_btn else '✗ ꜰᴀʟsᴇ'}</code>\n" \
              f"<b>›› ʀᴇᴘʟʏ ᴛᴇxᴛ:</b> <code>{client.reply_text if client.reply_text else 'ɴᴏɴᴇ'}</code>\n" \
              f"<b>›› ᴀʜᴍɪɴs:</b> <code>{len(client.admins)}</code>\n\n" \
              f"<b><u>≡ ᴍᴜʟᴛɪ sʜᴏʀᴛᴇɴᴇʀ sᴛᴀᴛᴜs:</u></b>\n" \
              f"<b>›› sʜᴏʀᴛɴᴇer 1:</b> <code>{getattr(config, 'SHORT_URL_1', 'None')}</code> [ <code>{'🟢 ᴏɴ' if getattr(config, 'SHORT_STATUS_1', True) else '🔴 ᴏғғ'}</code> ]\n" \
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
            [InlineKeyboardButton('ᴛᴇxᴛs', 'texts'), InlineKeyboardButton('🛠️ sʜᴏʀᴛɴᴇer sᴇᴛᴛɪɴgs', 'shortner')],
            [InlineKeyboardButton('‹ ᴘʀᴇᴠ', 'settings'), InlineKeyboardButton('ʜᴏᴍᴇ', 'home')]
        ])

    if edit and hasattr(query_or_message, 'message'):
        try:
            await query_or_message.message.edit_caption(caption=msg, reply_markup=markup)
        except Exception:
            try:
                await query_or_message.message.edit_text(text=msg, reply_markup=markup)
            except Exception:
                pass
    else:
        await query_or_message.reply_photo(photo=image_url, caption=msg, reply_markup=markup)

#===============================================================#
# 🚀 ROUTERS FOR COMMAND INTERFACES (/SETTINGS)
#===============================================================#

@Client.on_message(filters.command("settings") & filters.private)
async def settings_text_command(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    await render_settings_view(client, message, page=1, edit=False)

@Client.on_callback_query(filters.regex("^settings$"))
async def settings_callback(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    await query.answer()
    await render_settings_view(client, query, page=1, edit=True)

@Client.on_callback_query(filters.regex("^settings_page_2$"))
async def settings_page_2_callback(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    await query.answer()
    await render_settings_view(client, query, page=2, edit=True)

#===============================================================#
# 📲 HIGH-PRIORITY CORE CALLBACK MODULES (GLOBAL NAVIGATION FIX)
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
    
    try:
        await query.message.edit_media(
            media=InputMediaPhoto(media=config.MESSAGES.get("START_PHOTO", ""), caption=start_caption),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception:
        try:
            await query.message.edit_text(text=start_caption, reply_markup=InlineKeyboardMarkup(buttons))
        except Exception:
            pass

@Client.on_callback_query(filters.regex("^ABOUT$"))
async def render_about_callback_query(client: Client, query: CallbackQuery):
    await query.answer("ℹß Loading about documentation details...")
    about_text = config.MESSAGES.get('ABOUT', '').format(bot_name=client.username)
    back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data="home")]])
    try:
        await query.message.edit_caption(caption=about_text, reply_markup=back_markup)
    except Exception:
        await query.message.edit_text(text=about_text, reply_markup=back_markup)

@Client.on_callback_query(filters.regex("^close$"))
async def close_panel_callback_query(client: Client, query: CallbackQuery):
    await query.answer("🗑️ Interface closed.")
    await query.message.delete()

#===============================================================#
# 🛠️ SYSTEM CONFIG WORKING HANDLERS (ALL BUTTONS ACTION LAYER)
#===============================================================#

@Client.on_callback_query(filters.regex("^fsub$"))
async def fsub_callback(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    await query.answer()
    
    if client.fsub_dict:
        channel_list = []
        for channel_id, channel_data in client.fsub_dict.items():
            channel_name = channel_data[0] if channel_data and len(channel_data) > 0 else "Unknown"
            request_status = "✓ ʀᴇǫᴜᴇsᴛ" if channel_data[2] else "✗ ʀᴇǫᴜᴇsᴛ"
            timer_status = f"ᴛɪᴍᴇʀ: {channel_data[3]}ᴍ" if channel_data[3] > 0 else "ᴛɪᴍᴇʀ: ∞"
            channel_list.append(f"• <code>{channel_name}</code> (<code>{channel_id}</code>) - {request_status}, {timer_status}")
        channels_display = "\n".join(channel_list)
    else:
        channels_display = "_ɴᴏ ꜰᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ᴄʜᴀɴɴᴇʟs ᴄᴏɴғɪɢᴜʀᴇᴅ_"
    
    msg = f"<b>◍ ꜰᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ sᴇᴛᴛɪɴɢs</b>\n\n" \
          f"›› <b>ᴄᴏɴғɪɢᴜʀᴇᴅ ᴄʜᴀɴɴᴇʟs:</b>\n{channels_display}\n\n" \
          f"__<b>ᴜsᴇ ᴛʜᴇ ᴀᴘᴘʀᴏᴘʀɪᴀᴛᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴀᴅᴅ ᴏʀ ʀᴇᴍᴏᴠᴇ ᴀ ꜰᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ᴄʜᴀɴɴᴇʟ!</b>__"
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('›› ᴀᴅᴅ ᴄʜᴀɴɴᴇʟ', 'add_fsub'), InlineKeyboardButton('›› ʀᴇᴍᴏᴠᴇ ᴄʜᴀɴɴᴇʟ', 'rm_fsub')],
        [InlineKeyboardButton('‹ ʙᴀᴄᴋ', 'settings')]
    ])
    await query.message.edit_caption(caption=msg, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex("^db_channels$"))
async def db_channels_callback(client, query):
    if query.from_user.id not in client.admins: 
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    await query.answer()
    
    db_channels_data = getattr(client, 'db_channels', {})
    if db_channels_data:
        channel_list = []
        for channel_id_str, channel_data in db_channels_data.items():
            channel_name = channel_data.get('name', 'Unknown')
            is_primary = "✓ ᴘʀɪᴍᴀʀʏ" if channel_data.get('is_primary', False) else "• sᴇᴄᴏɴᴅᴀʀʏ"
            is_active = "✓ ᴀᴄᴛɪᴠᴇ" if channel_data.get('is_active', True) else "✗ ɪɴᴀᴄᴛɪᴠᴇ"
            channel_list.append(f"• <code>{channel_name}</code> (<code>{channel_id_str}</code>)\n  {is_primary} | {is_active}")
        channels_display = "\n\n".join(channel_list)
    else: 
        channels_display = "_ɴᴏ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟs ᴄᴏɴғɪɢᴜʀᴇᴅ_"
        
    primary_db = getattr(client, 'primary_db_channel', client.db)
    msg = f"<b>◍ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟs sᴇᴛᴛɪɴɢs</b>\n\n" \
          f"›› <b><b>ᴄᴜʀʀᴇɴᴛ ᴘʀɪᴍᴀʀʏ ᴅʙ:</b></b> <code>{primary_db}</code>\n" \
          f"›› <b><b><b>ᴛᴏᴛᴀʟ ᴅʙ ᴄʜᴀɴɴᴇʟs:</b></b></b> <code>{len(db_channels_data)}</code>\n\n" \
          f"**<b>ᴄᴏɴғɪɢᴜʀᴇᴅ ᴄʜᴀɴɴᴇʟs:</b>**\n{channels_display}"
          
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('›› ᴀᴅᴅ ᴅʙ ᴄʜᴀɴɴᴇʟ', 'add_db_channel'), InlineKeyboardButton('›› ʀᴇᴍᴏᴠᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ', 'rm_db_channel')],
        [InlineKeyboardButton('›› sᴇᴛ ᴘʀɪᴍᴀʀʏ', 'set_primary_db'), InlineKeyboardButton('›› sᴛᴀᴛᴜs', 'toggle_db_status')],
        [InlineKeyboardButton('‹ ʙᴀᴄᴋ', 'settings')]
    ])
    await query.message.edit_caption(caption=msg, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex("^(admins|auto_del|protect|photos|texts)$"))
async def core_backward_compatibility_redirects(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    
    action = query.data
    await query.answer(f"📁 Opening operational sub-layer: {action}")
    
    # Leverages existing logic mapping inside administrative modules seamlessly
    if action == "admins":
        from plugins.admins import admins as render_admin_panel
        await render_admin_panel(client, query)
    else:
        await query.answer("⚙️ Sub-feature configuration panel active via listener nodes.", show_alert=True)
    
